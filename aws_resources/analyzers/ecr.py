"""ECR analyzer

Summarizes ECR repositories and (optionally) per-repository image counts.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class ECRAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for ECRAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("ecr", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        paginator = self.client.get_paginator("describe_repositories")
        repos: List[Dict] = []
        total = 0
        for page in paginator.paginate():
            for r in page.get("repositories", []) or page.get("repositories") or []:
                repos.append({"name": r.get("repositoryName"), "uri": r.get("repositoryUri")})
                total += 1

        result = {"summary": {"total_repositories": total}}

        if include_details:
            # attempt to count images per repo (may be slow)
            details = []
            for r in repos:
                name = r.get("name")
                try:
                    resp = self.client.list_images(repositoryName=name)
                    images = resp.get("imageIds", [])
                    count = len(images)
                except Exception:
                    logger.debug("Failed to list images for %s", name, exc_info=True)
                    count = None
                details.append({"name": name, "uri": r.get("uri"), "image_count": count})
            result["repositories"] = details

        return result
