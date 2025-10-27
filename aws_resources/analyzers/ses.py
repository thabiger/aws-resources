"""SES analyzer

Summarizes SES identities (email/domain) and optionally returns verification
state for each identity when include_details=True.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class SESAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for SESAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("ses", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        # List identities by type (EmailAddress and Domain) because the API
        # validates IdentityType and doesn't accept a generic 'All' value.
        identities: List[str] = []
        for t in ("EmailAddress", "Domain"):
            try:
                resp = self.client.list_identities(IdentityType=t)
                identities.extend(resp.get("Identities", []))
            except Exception:
                logger.debug("list_identities failed for type %s", t, exc_info=True)

        # dedupe while preserving order
        seen = set()
        identities = [x for x in identities if not (x in seen or seen.add(x))]
        total = len(identities)
        result = {"summary": {"total_identities": total}}

        if include_details and identities:
            attrs = {}
            try:
                attrs = self.client.get_identity_verification_attributes(Identities=identities).get("VerificationAttributes", {})
            except Exception:
                logger.debug("Failed to get verification attributes", exc_info=True)

            out = []
            for i in identities:
                av = attrs.get(i, {})
                out.append({"identity": i, "verification_status": av.get("VerificationStatus"), "verification_token": av.get("VerificationToken")})
            result["identities"] = out

        return result
