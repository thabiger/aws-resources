"""SNS analyzer

Summarizes SNS topics and optionally returns per-topic attributes.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class SNSAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for SNSAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("sns", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        paginator = self.client.get_paginator("list_topics")
        topics: List[str] = []
        for page in paginator.paginate():
            for t in page.get("Topics", []) or []:
                topics.append(t.get("TopicArn"))

        result = {"summary": {"total_topics": len(topics)}}

        if include_details:
            details = []
            for arn in topics:
                try:
                    attrs = self.client.get_topic_attributes(TopicArn=arn).get("Attributes", {})
                except Exception:
                    logger.debug("Failed to get attributes for %s", arn, exc_info=True)
                    attrs = {}
                details.append({"topic_arn": arn, "attributes": attrs})
            result["topics"] = details

        return result
