"""ElastiCache analyzer

Summarizes ElastiCache clusters (Redis/Memcached). Optional details per-cluster.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class ElastiCacheAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for ElastiCacheAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("elasticache", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        paginator = self.client.get_paginator("describe_cache_clusters")
        clusters: List[Dict] = []
        engines: Dict[str, int] = {}
        per_type_counts: Dict[str, int] = {}
        total_nodes = 0

        for page in paginator.paginate(ShowCacheNodeInfo=True):
            for c in page.get("CacheClusters", []) or []:
                clusters.append(c)
                eng = c.get("Engine")
                engines[eng] = engines.get(eng, 0) + 1

                # determine node type and count
                node_type = c.get("CacheNodeType")
                node_count = c.get("NumCacheNodes") or len(c.get("CacheNodes", []) or [])

                # some responses may have node type per CacheNode; fall back accordingly
                if not node_type:
                    nodes = c.get("CacheNodes") or []
                    if nodes and isinstance(nodes, list):
                        node_type = nodes[0].get("CacheNodeType")

                # normalize: ElastiCache node types often are prefixed with 'cache.'
                norm_type = None
                if isinstance(node_type, str):
                    if node_type.startswith("cache."):
                        norm_type = node_type[len("cache."):]
                    else:
                        norm_type = node_type

                if norm_type:
                    per_type_counts[norm_type] = per_type_counts.get(norm_type, 0) + (node_count or 0)
                    total_nodes += (node_count or 0)

        summary: Dict[str, object] = {"total_clusters": len(clusters), "by_engine": engines}

        if per_type_counts:
            # enrich via EC2 DescribeInstanceTypes
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
            details = []
            for c in clusters:
                details.append({
                    "cache_cluster_id": c.get("CacheClusterId"),
                    "engine": c.get("Engine"),
                    "num_cache_nodes": c.get("NumCacheNodes"),
                    "status": c.get("CacheClusterStatus"),
                    "cache_node_type": c.get("CacheNodeType"),
                })
            result["clusters"] = details

        return result
