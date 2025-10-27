"""RDS analyzer

Collects RDS DB instances and provides basic enrichment (instance class, engine,
allocated storage) and a best-effort mapping from DB instance class to vCPU/memory
using a small static mapping for common classes. If a class is unknown the
vCPU/memory fields will be omitted (or zeroed) and the output will note limited
support.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:  # pragma: no cover - tests will inject a fake boto3
    boto3 = None  # type: ignore

logger = logging.getLogger(__name__)

# Small static mapping for common RDS instance classes to vCPU/memory (MiB).
# This is best-effort; not exhaustive. We also map DB instance class -> EC2
# instance type (e.g. db.t3.micro -> t3.micro) and will call EC2
# DescribeInstanceTypes to obtain authoritative vCPU/memory when possible.
STATIC_RDS_CLASS_MAP: Dict[str, Dict[str, int]] = {
    # family t3 (examples)
    "db.t3.micro": {"vCPU": 2, "memory_mib": 1024},
    "db.t3.small": {"vCPU": 2, "memory_mib": 2048},
    "db.t3.medium": {"vCPU": 2, "memory_mib": 4096},
    # common general purpose
    "db.m5.large": {"vCPU": 2, "memory_mib": 8192},
    "db.m5.xlarge": {"vCPU": 4, "memory_mib": 16384},
}

# Best-effort DB class -> EC2 instance type mapping. Many RDS classes map to
# the same-named EC2 instance type without the 'db.' prefix, but some mappings
# are more complex and can be added here.
DBCLASS_TO_EC2: Dict[str, str] = {
    "db.t3.micro": "t3.micro",
    "db.t3.small": "t3.small",
    "db.t3.medium": "t3.medium",
    "db.m5.large": "m5.large",
    "db.m5.xlarge": "m5.xlarge",
}


class RDSAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for RDSAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("rds", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        """Collect DB instances and return structured info and summary aggregates.

        Output shape (example):
        {
            "instances": [
                {"id": "db-1", "class": "db.t3.medium", "engine": "postgres", "allocated_storage_gib": 20, "vCPU": 2, "memory_mib": 4096}
            ],
            "summary": {"total_instances": 1, "total_allocated_storage_gib": 20, "total_vCPU": 2, "total_memory_mib": 4096}
        }
        """
        paginator = self.client.get_paginator("describe_db_instances")

        instances: List[Dict] = []
        total_allocated_storage = 0
        total_vcpu = 0
        total_memory = 0
        per_engine: Dict[str, int] = {}
        per_class: Dict[str, int] = {}

        for page in paginator.paginate():
            for db in page.get("DBInstances", []):
                identifier = db.get("DBInstanceIdentifier")
                clazz = db.get("DBInstanceClass")
                engine = db.get("Engine")
                status = db.get("DBInstanceStatus")
                multi_az = db.get("MultiAZ")
                allocated = db.get("AllocatedStorage") or 0
                endpoint = (db.get("Endpoint") or {}).get("Address")

                spec = STATIC_RDS_CLASS_MAP.get(clazz, {})
                v = spec.get("vCPU") or 0
                m = spec.get("memory_mib") or 0

                instances.append({
                    "id": identifier,
                    "class": clazz,
                    "engine": engine,
                    "status": status,
                    "multi_az": multi_az,
                    "allocated_storage_gib": allocated,
                    "endpoint": endpoint,
                    "vCPU": v,
                    "memory_mib": m,
                    "mapping_supported": bool(spec),
                })

                total_allocated_storage += allocated
                total_vcpu += v
                total_memory += m

                if engine:
                    per_engine[engine] = per_engine.get(engine, 0) + 1
                if clazz:
                    per_class[clazz] = per_class.get(clazz, 0) + 1

        # Try to enrich vCPU/memory using EC2 DescribeInstanceTypes when we can
        # map DB classes to EC2 instance types.
        db_classes = list(per_class.keys())
        ec2_types_needed = set()
        db_to_ec2: Dict[str, str] = {}
        for c in db_classes:
            ec2_t = DBCLASS_TO_EC2.get(c)
            if not ec2_t:
                # fallback: strip leading 'db.' if present
                if c.startswith("db."):
                    ec2_t = c[3:]
            if ec2_t:
                db_to_ec2[c] = ec2_t
                ec2_types_needed.add(ec2_t)

        type_specs: Dict[str, Dict[str, int]] = {}
        if ec2_types_needed:
            # call EC2 DescribeInstanceTypes to get authoritative specs
            ec2_client = self.session.client("ec2", region_name=self.region_name)
            itypes_list = list(ec2_types_needed)
            for i in range(0, len(itypes_list), 100):
                chunk = itypes_list[i : i + 100]
                try:
                    resp = ec2_client.describe_instance_types(InstanceTypes=chunk)
                    for it in resp.get("InstanceTypes", []):
                        name = it.get("InstanceType")
                        vcpu = it.get("VCpuInfo", {}).get("DefaultVCpus") or 0
                        mem_mib = it.get("MemoryInfo", {}).get("SizeInMiB") or 0
                        type_specs[name] = {"vCPU": vcpu, "memory_mib": mem_mib}
                except Exception:
                    logger.exception("Failed to describe EC2 instance types for %s", chunk)

        # Now rebuild instances list to set vCPU/memory using EC2 type mapping when
        # available; otherwise fall back to STATIC_RDS_CLASS_MAP.
        enriched_instances: List[Dict] = []
        total_allocated_storage = 0
        total_vcpu = 0
        total_memory = 0
        for inst in instances:
            clazz = inst.get("class")
            v = 0
            m = 0
            mapped_ec2 = db_to_ec2.get(clazz)
            if mapped_ec2 and mapped_ec2 in type_specs:
                spec = type_specs[mapped_ec2]
                v = spec.get("vCPU", 0)
                m = spec.get("memory_mib", 0)
            else:
                spec = STATIC_RDS_CLASS_MAP.get(clazz, {})
                v = spec.get("vCPU", 0)
                m = spec.get("memory_mib", 0)

            enriched = {**inst, "vCPU": v, "memory_mib": m, "ec2_instance_type": mapped_ec2}
            enriched_instances.append(enriched)

            total_allocated_storage += inst.get("allocated_storage_gib", 0)
            total_vcpu += v
            total_memory += m

        result: Dict[str, object] = {
            "summary": {
                "total_instances": len(enriched_instances),
                "total_allocated_storage_gib": total_allocated_storage,
                "total_vCPU": total_vcpu,
                "total_memory_mib": total_memory,
                "by_engine": per_engine,
                "by_class": per_class,
            },
        }

        if include_details:
            result["instances"] = enriched_instances

        return result
