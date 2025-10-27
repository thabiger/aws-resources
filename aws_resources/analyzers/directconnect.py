"""Direct Connect analyzer

Summarizes AWS Direct Connect connections. Lightweight summary only by default
with optional per-connection details.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class DirectConnectAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for DirectConnectAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        # Direct Connect is a regional/global service; client name 'directconnect'
        self.client = self.session.client("directconnect", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        try:
            resp = self.client.describe_connections()
            conns = resp.get("connections", []) or resp.get("connections") or []
        except Exception:
            conns = []

        result = {"summary": {"total_connections": len(conns)}}

        if include_details and conns:
            details = []
            for c in conns:
                details.append({"connectionId": c.get("connectionId"), "location": c.get("location"), "bandwidth": c.get("bandwidth"), "connectionState": c.get("connectionState")})
            result["connections"] = details

        return result
