"""Route53 analyzer

Summarizes hosted zones and optionally returns basic zone info.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class Route53Analyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        # Route53 is global; region_name unused
        self.profile = profile
        if boto3 is None:
            raise RuntimeError("boto3 is required for Route53Analyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("route53")

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        resp = self.client.list_hosted_zones()
        zones = resp.get("HostedZones", [])
        total = len(zones)
        private_count = sum(1 for z in zones if z.get("Config", {}).get("PrivateZone") is True)
        public_count = total - private_count
        result = {
            "summary": {
                "total_hosted_zones": total,
                "by_type": {"public": public_count, "private": private_count},
            }
        }

        if include_details:
            out = []
            for z in zones:
                out.append({"id": z.get("Id"), "name": z.get("Name"), "private": z.get("Config", {}).get("PrivateZone")})
            result["hosted_zones"] = out

        return result
