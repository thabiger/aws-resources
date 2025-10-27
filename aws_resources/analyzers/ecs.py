"""ECS analyzer

Summarizes ECS clusters and counts services/tasks.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class ECSAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for ECSAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("ecs", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        paginator = self.client.get_paginator("list_clusters")
        clusters: List[str] = []
        for page in paginator.paginate():
            clusters.extend(page.get("clusterArns") or [])

        total_clusters = len(clusters)
        result = {"summary": {"total_clusters": total_clusters}}

        if include_details:
            details = []
            for arn in clusters:
                try:
                    desc = self.client.describe_clusters(clusters=[arn]).get("clusters", [])[0]
                    services = self.client.list_services(cluster=arn).get("serviceArns", [])
                    tasks = self.client.list_tasks(cluster=arn).get("taskArns", [])
                    details.append({"cluster_arn": arn, "status": desc.get("status"), "service_count": len(services), "task_count": len(tasks)})
                except Exception:
                    logger.debug("Failed to describe cluster %s", arn, exc_info=True)
                    details.append({"cluster_arn": arn, "status": "unknown"})
            result["clusters"] = details

        return result
