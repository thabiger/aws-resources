"""SQS analyzer

Summarizes SQS queues and optionally returns per-queue attributes.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class SQSAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for SQSAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("sqs", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        resp = self.client.list_queues()
        urls = resp.get("QueueUrls", [])
        total = len(urls)
        result = {"summary": {"total_queues": total}}

        if include_details and urls:
            details = []
            for u in urls:
                try:
                    attrs = self.client.get_queue_attributes(QueueUrl=u, AttributeNames=["All"]).get("Attributes", {})
                except Exception:
                    logger.debug("Failed to get attributes for %s", u, exc_info=True)
                    attrs = {}
                details.append({"queue_url": u, "attributes": attrs})
            result["queues"] = details

        return result
