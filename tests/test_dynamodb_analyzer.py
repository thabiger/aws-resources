import sys
import unittest
from unittest.mock import MagicMock, patch


class TestDynamoDBAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_dynamodb_summary_and_details(self):
        import boto3

        mock_client = MagicMock()

        # list_tables paginator
        mock_client.get_paginator.return_value.paginate.return_value = [
            {"TableNames": ["table-a", "table-b"]}
        ]

        # describe_table responses
        def describe_table(TableName=None):
            if TableName == "table-a":
                return {
                    "Table": {
                        "TableName": "table-a",
                        "TableStatus": "ACTIVE",
                        "ItemCount": 10,
                        "TableSizeBytes": 1024,
                        "BillingModeSummary": {"BillingMode": "PAY_PER_REQUEST"},
                    }
                }
            else:
                return {
                    "Table": {
                        "TableName": "table-b",
                        "TableStatus": "ACTIVE",
                        "ItemCount": 5,
                        "TableSizeBytes": 512,
                        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 2},
                    }
                }

        mock_client.describe_table.side_effect = describe_table

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.dynamodb import DynamoDBAnalyzer

        a = DynamoDBAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_tables"], 2)
        self.assertIn("unknown", out["summary"]["by_billing_mode"])

        out2 = a.analyze(include_details=True)
        self.assertEqual(out2["summary"]["total_tables"], 2)
        self.assertIn("PAY_PER_REQUEST", out2["summary"]["by_billing_mode"])
        self.assertIn("PROVISIONED", out2["summary"]["by_billing_mode"])
        self.assertIn("tables", out2)
        self.assertEqual(len(out2["tables"]), 2)
        self.assertEqual(out2["tables"][0]["name"], "table-a")
        # provisioned capacity totals should sum provisioned table RCUs/WCUs
        self.assertEqual(out2["summary"]["provisioned_read_capacity_units_total"], 5)
        self.assertEqual(out2["summary"]["provisioned_write_capacity_units_total"], 2)


if __name__ == "__main__":
    unittest.main()
