"""EKS analyzer

Summarizes EKS clusters and optionally returns per-cluster details.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class EKSAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for EKSAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("eks", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        paginator = self.client.get_paginator("list_clusters")
        clusters: List[str] = []
        for page in paginator.paginate():
            clusters.extend(page.get("clusters") or [])

        result = {"summary": {"total_clusters": len(clusters)}}

        if include_details:
            details = []
            for name in clusters:
                try:
                    info = self.client.describe_cluster(name=name).get("cluster", {})
                    details.append({"name": name, "status": info.get("status"), "version": info.get("version")})
                except Exception:
                    logger.debug("Failed to describe EKS cluster %s", name, exc_info=True)
                    details.append({"name": name, "status": "unknown"})
            result["clusters"] = details

        return result
