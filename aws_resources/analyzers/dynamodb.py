"""DynamoDB analyzer

Summary by default: total table count and counts by billing mode (PROVISIONED vs PAY_PER_REQUEST).
When include_details=True the analyzer will call DescribeTable for each table and
return per-table metadata: table name, status, billing mode, item count, table size bytes,
and provisioned throughput if applicable.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:  # pragma: no cover - tests inject a fake boto3
    boto3 = None  # type: ignore

logger = logging.getLogger(__name__)


class DynamoDBAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for DynamoDBAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("dynamodb", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        paginator = self.client.get_paginator("list_tables")

        table_names: List[str] = []
        for page in paginator.paginate():
            names = page.get("TableNames") or []
            table_names.extend(names)

        total = len(table_names)
        by_billing: Dict[str, int] = {}
        tables: List[Dict] = []

        if include_details and table_names:
            # Describe each table to collect metadata. This can be a bit chatty but
            # is acceptable for small numbers of tables and when user explicitly
            # asks for details.
            for t in table_names:
                try:
                    resp = self.client.describe_table(TableName=t)
                    table = resp.get("Table", {})
                    billing = (table.get("BillingModeSummary") or {}).get("BillingMode") or "PROVISIONED"
                    item_count = table.get("ItemCount")
                    size_bytes = table.get("TableSizeBytes")
                    prov = table.get("ProvisionedThroughput") or {}

                    tables.append({
                        "name": t,
                        "status": table.get("TableStatus"),
                        "billing_mode": billing,
                        "item_count": item_count,
                        "table_size_bytes": size_bytes,
                        "provisioned_throughput": {
                            "read_capacity_units": prov.get("ReadCapacityUnits"),
                            "write_capacity_units": prov.get("WriteCapacityUnits"),
                        },
                    })

                    by_billing[billing] = by_billing.get(billing, 0) + 1
                except Exception:
                    logger.exception("Failed to describe DynamoDB table %s", t)
                    by_billing["unknown"] = by_billing.get("unknown", 0) + 1
        else:
            # only produce billing-mode counts by sampling via DescribeTable is expensive
            # so we default to unknown when details are not requested
            by_billing["unknown"] = total

        result: Dict[str, object] = {
            "summary": {
                "total_tables": total,
                "by_billing_mode": by_billing,
            }
        }

        if include_details:
            result["tables"] = tables

            # compute provisioned capacity totals (best-effort)
            total_provisioned_read = 0
            total_provisioned_write = 0
            for tb in tables:
                if tb.get("billing_mode") == "PROVISIONED":
                    prov = tb.get("provisioned_throughput") or {}
                    r = prov.get("read_capacity_units") or 0
                    w = prov.get("write_capacity_units") or 0
                    total_provisioned_read += r
                    total_provisioned_write += w

            result["summary"]["provisioned_read_capacity_units_total"] = total_provisioned_read
            result["summary"]["provisioned_write_capacity_units_total"] = total_provisioned_write

        return result
