"""DocumentDB analyzer

Summarizes Amazon DocumentDB (with MongoDB compatibility) clusters and nodes.

This is best-effort:
- lists DB clusters via the `docdb` client
- lists DB instances via the `docdb` client and groups them by cluster
- derives instance-class -> EC2 instance type by stripping leading "db." where appropriate
- calls EC2 DescribeInstanceTypes to enrich vCPU/memory per instance type
- returns summary with total_clusters, total_nodes, by_instance_class and best-effort total_vCPU/total_memory_mib

The analyzer keeps detailed per-cluster and per-instance lists when `include_details=True`.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:  # pragma: no cover - tests inject a fake boto3
    boto3 = None  # type: ignore

logger = logging.getLogger(__name__)


class DocumentDBAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for DocumentDBAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("docdb", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        # list clusters
        try:
            paginator = self.client.get_paginator("describe_db_clusters")
            clusters: List[Dict] = []
            for page in paginator.paginate():
                clusters.extend(page.get("DBClusters", []) or [])
        except Exception:
            # fallback: call describe_db_clusters once
            try:
                resp = self.client.describe_db_clusters()
                clusters = resp.get("DBClusters", [])
            except Exception:
                logger.exception("Failed to list DocumentDB clusters")
                clusters = []

        # list instances and group by cluster
        instances: List[Dict] = []
        try:
            paginator = self.client.get_paginator("describe_db_instances")
            for page in paginator.paginate():
                instances.extend(page.get("DBInstances", []) or [])
        except Exception:
            try:
                resp = self.client.describe_db_instances()
                instances = resp.get("DBInstances", [])
            except Exception:
                logger.debug("Failed to list DocumentDB instances", exc_info=True)
                instances = []

        # map cluster identifier -> instances
        cluster_to_instances: Dict[str, List[Dict]] = {}
        for inst in instances:
            cluster = inst.get("DBClusterIdentifier") or inst.get("DBClusterId") or inst.get("DBClusterIdentifier")
            if cluster:
                cluster_to_instances.setdefault(cluster, []).append(inst)

        total_clusters = len(clusters)
        total_nodes = sum(len(cluster_to_instances.get(c.get("DBClusterIdentifier") or c.get("DBClusterId"), [])) for c in clusters)

        # compute per-instance-class counts
        per_class_counts: Dict[str, int] = {}
        for inst in instances:
            clazz = inst.get("DBInstanceClass") or inst.get("InstanceClass")
            if clazz:
                per_class_counts[clazz] = per_class_counts.get(clazz, 0) + 1

        summary: Dict[str, object] = {"total_clusters": total_clusters, "total_nodes": total_nodes, "by_instance_class": per_class_counts}

        # try to enrich instance-class -> ec2 instance type and get vCPU/memory
        if per_class_counts:
            # derive EC2 instance types (best-effort): strip leading 'db.' if present
            ec2_types = set()
            class_to_ec2: Dict[str, str] = {}
            for c in list(per_class_counts.keys()):
                ec2_t = None
                if c.startswith("db."):
                    ec2_t = c[3:]
                else:
                    ec2_t = c
                class_to_ec2[c] = ec2_t
                if ec2_t:
                    ec2_types.add(ec2_t)

            type_specs: Dict[str, Dict[str, int]] = {}
            if ec2_types:
                ec2_client = self.session.client("ec2", region_name=self.region_name)
                itypes = list(ec2_types)
                for i in range(0, len(itypes), 100):
                    chunk = itypes[i : i + 100]
                    try:
                        resp = ec2_client.describe_instance_types(InstanceTypes=chunk)
                        for it in resp.get("InstanceTypes", []):
                            name = it.get("InstanceType")
                            vcpu = it.get("VCpuInfo", {}).get("DefaultVCpus") or 0
                            mem_mib = it.get("MemoryInfo", {}).get("SizeInMiB") or 0
                            type_specs[name] = {"vCPU": vcpu, "memory_mib": mem_mib}
                    except Exception:
                        logger.exception("Failed to describe EC2 instance types for %s", chunk)

            # build by_instance_type summary using mapped ec2 types
            by_instance_type: Dict[str, Dict[str, int]] = {}
            total_vcpu = 0
            total_memory = 0
            for cls, count in per_class_counts.items():
                ec2_t = class_to_ec2.get(cls)
                spec = type_specs.get(ec2_t, {})
                v_each = spec.get("vCPU", 0)
                m_each = spec.get("memory_mib", 0)
                by_instance_type[ec2_t or cls] = {
                    "count": count,
                    "vCPU_each": v_each,
                    "memory_mib_each": m_each,
                    "vCPU_total": v_each * count,
                    "memory_mib_total": m_each * count,
                }
                total_vcpu += v_each * count
                total_memory += m_each * count

            summary.update({"total_vCPU": total_vcpu, "total_memory_mib": total_memory, "by_instance_type": by_instance_type})

        result: Dict[str, object] = {"summary": summary}

        if include_details:
            # include per-cluster and per-instance lists
            details = []
            for c in clusters:
                cid = c.get("DBClusterIdentifier") or c.get("DBClusterId")
                details.append({
                    "cluster_identifier": cid,
                    "engine": c.get("Engine"),
                    "status": c.get("Status") or c.get("DBClusterStatus"),
                    "instance_count": len(cluster_to_instances.get(cid, [])),
                    "instances": [
                        {
                            "instance_id": i.get("DBInstanceIdentifier") or i.get("DBInstanceId"),
                            "class": i.get("DBInstanceClass"),
                            "endpoint": (i.get("Endpoint") or {}).get("Address"),
                            "status": i.get("DBInstanceStatus") or i.get("DBInstanceStatus"),
                        }
                        for i in cluster_to_instances.get(cid, [])
                    ],
                })
            result["clusters"] = details
            result["instances"] = instances

        return result
