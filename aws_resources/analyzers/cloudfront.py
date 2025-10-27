"""CloudFront analyzer

Provides a lightweight inventory of CloudFront distributions. By default returns
a summary with total distributions and enabled/disabled counts. When
include_details=True returns a list of distributions with basic metadata.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:  # pragma: no cover - tests inject a fake boto3
    boto3 = None  # type: ignore

logger = logging.getLogger(__name__)


class CloudFrontAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        # CloudFront is a global service; region_name is not required but kept
        # for API compatibility with other analyzers.
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for CloudFrontAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("cloudfront")

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        paginator = self.client.get_paginator("list_distributions")

        total = 0
        enabled = 0
        disabled = 0
        distributions: List[Dict] = []

        for page in paginator.paginate():
            # Older SDKs wrap distributions under 'DistributionList'
            dist_list = page.get("DistributionList") or page
            items = dist_list.get("Items") if isinstance(dist_list, dict) else None
            if items is None:
                # Try top-level Items
                items = page.get("Items") or []

            for d in items or []:
                total += 1
                if d.get("Enabled"):
                    enabled += 1
                else:
                    disabled += 1

                distributions.append({
                    "id": d.get("Id"),
                    "domain_name": d.get("DomainName"),
                    "enabled": bool(d.get("Enabled")),
                    "origins_count": len((d.get("Origins") or {}).get("Items", [])),
                    "aliases_count": len((d.get("Aliases") or {}).get("Items", [])),
                    "comment": d.get("Comment"),
                })

        result: Dict[str, object] = {
            "summary": {
                "total_distributions": total,
                "enabled": enabled,
                "disabled": disabled,
            }
        }

        if include_details:
            result["distributions"] = distributions

        return result
