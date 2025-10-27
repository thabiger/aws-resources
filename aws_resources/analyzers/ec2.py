"""EC2 analyzer

Collects EC2 instances and enriches instance types with vCPU and memory using DescribeInstanceTypes.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:  # pragma: no cover - tests will inject a fake boto3
    boto3 = None  # type: ignore

logger = logging.getLogger(__name__)


class EC2Analyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for EC2Analyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("ec2", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        """Return dict with per-instance details and aggregated totals.

        Output shape (example):
        {
            "instances": [{"instance_id": "i-...", "type": "t3.medium", "vCPU": 2, "memory_mib": 4096, "state": "running"}, ...],
            "summary": {"total_instances": 3, "total_vCPU": 8, "total_memory_mib": 16384}
        }
        """
        paginator = self.client.get_paginator("describe_instances")

        instances: List[Dict] = []
        instance_types = set()

        for page in paginator.paginate():
            for r in page.get("Reservations", []):
                for i in r.get("Instances", []):
                    iid = i.get("InstanceId")
                    itype = i.get("InstanceType")
                    state = i.get("State", {}).get("Name")
                    # InstanceLifecycle is "spot" for Spot Instances; default to on_demand otherwise
                    lifecycle = "spot" if i.get("InstanceLifecycle") == "spot" else "on_demand"
                    # Prefer instance-level Architecture if present (values like 'x86_64' or 'arm64')
                    inst_arch_raw = i.get("Architecture")
                    if inst_arch_raw:
                        raw = str(inst_arch_raw).lower()
                        if "arm" in raw or "aarch64" in raw:
                            inst_arch = "arm"
                        elif "x86" in raw or "amd64" in raw or "x86_64" in raw:
                            inst_arch = "x86"
                        else:
                            inst_arch = "unknown"
                    else:
                        inst_arch = None

                    instances.append({
                        "instance_id": iid,
                        "type": itype,
                        "state": state,
                        "lifecycle": lifecycle,
                        "architecture": inst_arch,
                    })
                    if itype:
                        instance_types.add(itype)

        # Fetch instance type specs in batches
        type_specs: Dict[str, Dict] = {}
        if instance_types:
            itypes_list = list(instance_types)
            # describe_instance_types accepts up to 100 types at once
            for i in range(0, len(itypes_list), 100):
                chunk = itypes_list[i : i + 100]
                resp = self.client.describe_instance_types(InstanceTypes=chunk)
                for it in resp.get("InstanceTypes", []):
                    name = it.get("InstanceType")
                    vcpu = it.get("VCpuInfo", {}).get("DefaultVCpus")
                    mem_mib = it.get("MemoryInfo", {}).get("SizeInMiB")
                    # Determine primary architecture: prefer arm if present, otherwise x86
                    proc = it.get("ProcessorInfo", {})
                    supported = proc.get("SupportedArchitectures") or []
                    arch = None
                    if supported:
                        # Normalize common values
                        if "arm64" in supported or "aarch64" in supported:
                            arch = "arm"
                        else:
                            arch = "x86"
                    else:
                        arch = "unknown"

                    type_specs[name] = {"vCPU": vcpu, "memory_mib": mem_mib, "architecture": arch}

        total_vcpu = 0
        total_memory = 0
        spot_vcpu = 0
        spot_memory = 0
        ondemand_vcpu = 0
        ondemand_memory = 0
        enriched = []

        # per-architecture aggregates
        arch_summary: Dict[str, Dict[str, int]] = {}
        lifecycle_by_arch: Dict[str, Dict[str, int]] = {}

        for inst in instances:
            t = inst.get("type")
            spec = type_specs.get(t, {})
            v = spec.get("vCPU") or 0
            m = spec.get("memory_mib") or 0
            # prefer instance-level architecture measurement when available
            arch = inst.get("architecture") or spec.get("architecture", "unknown")
            total_vcpu += v
            total_memory += m
            enriched.append({**inst, "vCPU": v, "memory_mib": m, "architecture": arch})

            # add to lifecycle buckets
            if inst.get("lifecycle") == "spot":
                spot_vcpu += v
                spot_memory += m
            else:
                ondemand_vcpu += v
                ondemand_memory += m

            # update architecture summary
            if arch not in arch_summary:
                arch_summary[arch] = {"count": 0, "vCPU": 0, "memory_mib": 0}
            arch_summary[arch]["count"] += 1
            arch_summary[arch]["vCPU"] += v
            arch_summary[arch]["memory_mib"] += m

            # update lifecycle-by-architecture
            if arch not in lifecycle_by_arch:
                lifecycle_by_arch[arch] = {
                    "spot_count": 0,
                    "on_demand_count": 0,
                    "spot_vCPU": 0,
                    "spot_memory_mib": 0,
                    "on_demand_vCPU": 0,
                    "on_demand_memory_mib": 0,
                }
            if inst.get("lifecycle") == "spot":
                lifecycle_by_arch[arch]["spot_count"] += 1
                lifecycle_by_arch[arch]["spot_vCPU"] += v
                lifecycle_by_arch[arch]["spot_memory_mib"] += m
            else:
                lifecycle_by_arch[arch]["on_demand_count"] += 1
                lifecycle_by_arch[arch]["on_demand_vCPU"] += v
                lifecycle_by_arch[arch]["on_demand_memory_mib"] += m

        # lifecycle breakdown
        total_spot = sum(1 for i in enriched if i.get("lifecycle") == "spot")
        total_on_demand = sum(1 for i in enriched if i.get("lifecycle") == "on_demand")

        result: Dict[str, object] = {
            "summary": {
                "total_instances": len(instances),
                "total_vCPU": total_vcpu,
                "total_memory_mib": total_memory,
                "total_spot": total_spot,
                "total_on_demand": total_on_demand,
                "spot": {
                    "vCPU": spot_vcpu,
                    "memory_mib": spot_memory,
                },
                "ondemand": {
                    "vCPU": ondemand_vcpu,
                    "memory_mib": ondemand_memory,
                },
                "architecture": arch_summary,
                "lifecycle_by_architecture": lifecycle_by_arch,
            },
        }

        if include_details:
            result["instances"] = enriched

        return result
