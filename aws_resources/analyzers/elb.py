"""ELB analyzer

Summarizes Classic/ALB/NLB load balancers via elb and elbv2 APIs.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class ELBAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for ELBAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client_v1 = self.session.client("elb", region_name=region_name)
        self.client_v2 = self.session.client("elbv2", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        # Classic ELB
        try:
            v1 = self.client_v1.describe_load_balancers().get("LoadBalancerDescriptions", [])
        except Exception:
            v1 = []

        # ALB/NLB
        try:
            v2 = self.client_v2.describe_load_balancers().get("LoadBalancers", [])
        except Exception:
            v2 = []

        summary = {"classic": len(v1), "alb_nlb": len(v2), "total": len(v1) + len(v2)}
        result = {"summary": summary}

        if include_details:
            details = {"classic": [], "alb_nlb": []}
            for l in v1:
                details["classic"].append({"name": l.get("LoadBalancerName"), "dns": l.get("DNSName")})
            for l in v2:
                details["alb_nlb"].append({"arn": l.get("LoadBalancerArn"), "dns": l.get("DNSName"), "type": l.get("Type")})
            result["load_balancers"] = details

        return result
