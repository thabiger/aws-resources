"""OpenSearch (Elasticsearch) analyzer

Summarizes OpenSearch domains. Optional per-domain details.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class OpenSearchAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for OpenSearchAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        # older service name is 'es', newer is 'opensearch'
        try:
            self.client = self.session.client("opensearch", region_name=region_name)
        except Exception:
            self.client = self.session.client("es", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        # list domain names
        try:
            resp = self.client.list_domain_names()
            names = [d.get("DomainName") for d in resp.get("DomainNames", [])]
        except Exception:
            # fallback for es client
            try:
                resp = self.client.list_domain_names()
                names = [d.get("DomainName") for d in resp.get("DomainNames", [])]
            except Exception:
                names = []

        # collect per-domain details and cluster config where available
        domains_info = []
        if names:
            for n in names:
                try:
                    d = self.client.describe_domains(DomainNames=[n]).get("DomainStatusList", [])[0]
                    domains_info.append(d)
                except Exception:
                    logger.debug("Failed to describe domain %s", n, exc_info=True)

        # Extract instance-type counts from domain cluster configs
        per_type_counts: Dict[str, int] = {}
        total_nodes = 0
        domain_details: List[Dict] = []
        for d in domains_info:
            # cluster config key varies between 'ClusterConfig' and older 'ElasticsearchClusterConfig'
            cfg = d.get("ClusterConfig") or d.get("ElasticsearchClusterConfig") or {}
            inst_type = cfg.get("InstanceType") or cfg.get("InstanceType")
            inst_count = cfg.get("InstanceCount") or cfg.get("InstanceCount") or 0
            # OpenSearch instance types often have a suffix like '.search' (e.g. 'm5.large.search')
            if isinstance(inst_type, str) and inst_type.endswith(".search"):
                norm_type = inst_type[: -len(".search")]
            else:
                norm_type = inst_type

            if norm_type:
                per_type_counts[norm_type] = per_type_counts.get(norm_type, 0) + (inst_count or 0)
                total_nodes += (inst_count or 0)

            domain_details.append({
                "domain_name": d.get("DomainName"),
                "endpoint": d.get("Endpoint"),
                "cluster_config": {
                    "instance_type": inst_type,
                    "instance_count": inst_count,
                    "warm_type": cfg.get("WarmType") or cfg.get("WarmEnabled"),
                },
            })

        summary: Dict[str, object] = {"total_domains": len(names)}

        if per_type_counts:
            # try to enrich instance types via EC2 DescribeInstanceTypes
            ec2_client = self.session.client("ec2", region_name=self.region_name)
            type_specs: Dict[str, Dict[str, int]] = {}
            itypes = list(per_type_counts.keys())
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

            # build by_instance_type summary
            by_instance_type: Dict[str, Dict[str, int]] = {}
            total_vcpu = 0
            total_memory = 0
            for t, count in per_type_counts.items():
                spec = type_specs.get(t, {})
                v_each = spec.get("vCPU", 0)
                m_each = spec.get("memory_mib", 0)
                by_instance_type[t] = {
                    "count": count,
                    "vCPU_each": v_each,
                    "memory_mib_each": m_each,
                    "vCPU_total": v_each * count,
                    "memory_mib_total": m_each * count,
                }
                total_vcpu += v_each * count
                total_memory += m_each * count

            summary.update({
                "total_nodes": total_nodes,
                "total_vCPU": total_vcpu,
                "total_memory_mib": total_memory,
                "by_instance_type": by_instance_type,
            })
        else:
            summary.update({"total_nodes": total_nodes})

        result = {"summary": summary}

        if include_details:
            result["domains"] = domain_details

        return result
