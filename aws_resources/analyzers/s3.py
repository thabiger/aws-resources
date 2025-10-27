"""S3 analyzer

Provides a lightweight inventory of S3 buckets. By default returns a summary
with total bucket count. When include_details=True the analyzer returns a
list of buckets with basic metadata (name, creation_date, region). We do not
attempt to list objects or compute bucket sizes here because that can be
expensive; instead we note that size/object counts are not collected and point
to CloudWatch / S3 Inventory for authoritative metrics.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:  # pragma: no cover - tests inject a fake boto3
    boto3 = None  # type: ignore

logger = logging.getLogger(__name__)


class S3Analyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for S3Analyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("s3", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        resp = self.client.list_buckets()
        buckets = resp.get("Buckets", [])

        summary: Dict[str, object] = {"total_buckets": len(buckets)}
        result: Dict[str, object] = {"summary": summary}

        if include_details:
            out: List[Dict] = []
            for b in buckets:
                name = b.get("Name")
                created = b.get("CreationDate")
                region = None
                try:
                    loc = self.client.get_bucket_location(Bucket=name)
                    # LocationConstraint is None for us-east-1 in older APIs
                    region = loc.get("LocationConstraint") or "us-east-1"
                except Exception:
                    logger.debug("Failed to get location for bucket %s", name, exc_info=True)

                out.append({
                    "name": name,
                    "creation_date": str(created),
                    "region": region,
                    # Not collected here to avoid expensive listing; leave None
                    "size_bytes": None,
                    "object_count": None,
                    "note": "Size/object count not collected; use CloudWatch metrics or S3 Inventory for metrics.",
                })

            result["buckets"] = out

        return result
