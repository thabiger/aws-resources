"""KMS analyzer

Summarizes KMS keys and optionally returns per-key metadata.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class KMSAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for KMSAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("kms", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        paginator = self.client.get_paginator("list_keys")
        keys: List[str] = []
        for page in paginator.paginate():
            for k in page.get("Keys", []) or []:
                keys.append(k.get("KeyId") or k.get("KeyArn"))

        result = {"summary": {"total_keys": len(keys)}}

        if include_details and keys:
            details = []
            for kid in keys:
                try:
                    info = self.client.describe_key(KeyId=kid).get("KeyMetadata", {})
                except Exception:
                    logger.debug("Failed to describe key %s", kid, exc_info=True)
                    info = {}
                details.append({"key_id": kid, "description": info.get("Description"), "key_state": info.get("KeyState")})
            result["keys"] = details

        return result
