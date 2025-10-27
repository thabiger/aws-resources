"""Cost Explorer collector

Provides a small wrapper to query AWS Cost Explorer and return a list of services and their costs
for a given time period.
"""
from __future__ import annotations

from typing import List, Dict, Optional
import logging

import boto3

logger = logging.getLogger(__name__)


class CostExplorerCollector:
    """Simple wrapper around AWS Cost Explorer GetCostAndUsage.

    Methods:
        get_service_costs(start: str, end: str, profile: Optional[str]) -> List[Dict]
    """

    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        # Cost Explorer is a global service; boto3 will pick a region automatically but allow override
        self.client = self.session.client("ce", region_name=region_name)

    def get_service_costs(self, start: str, end: str, granularity: str = "MONTHLY") -> List[Dict[str, object]]:
        """Query Cost Explorer and return a list of services with cost totals.

        Args:
            start: YYYY-MM-DD
            end: YYYY-MM-DD
            granularity: MONTHLY | DAILY | HOURLY (CE supports MONTHLY or DAILY typically)

        Returns:
            List of dicts: {"service": str, "amount": float, "unit": str}
        """
        results: Dict[str, Dict[str, object]] = {}

        next_token = None
        while True:
            kwargs = {
                "TimePeriod": {"Start": start, "End": end},
                "Granularity": granularity,
                "Metrics": ["UnblendedCost"],
                "GroupBy": [{"Type": "DIMENSION", "Key": "SERVICE"}],
            }
            if next_token:
                kwargs["NextPageToken"] = next_token

            logger.debug("Calling GetCostAndUsage with %s", kwargs)
            resp = self.client.get_cost_and_usage(**kwargs)

            # Parse results
            for period in resp.get("ResultsByTime", []):
                groups = period.get("Groups", [])
                for g in groups:
                    keys = g.get("Keys", [])
                    service_name = keys[0] if keys else "Unknown"
                    metrics = g.get("Metrics", {})
                    ub = metrics.get("UnblendedCost", {})
                    amount = float(ub.get("Amount", "0") or 0)
                    unit = ub.get("Unit", "USD")

                    if service_name not in results:
                        results[service_name] = {"amount": 0.0, "unit": unit}
                    results[service_name]["amount"] += amount

            next_token = resp.get("NextPageToken")
            if not next_token:
                break

        # Convert to list
        out = []
        for svc, v in sorted(results.items(), key=lambda kv: kv[0].lower()):
            out.append({"service": svc, "amount": v["amount"], "unit": v.get("unit", "USD")})

        return out
