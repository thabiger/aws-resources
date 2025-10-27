import sys
import unittest
from unittest.mock import MagicMock, patch


class TestCostExplorerCollector(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_get_service_costs_pagination(self):
        # boto3 module exists as a MagicMock in sys.modules thanks to patch.dict
        import boto3
        # Mock client and responses
        mock_client = MagicMock()

        # First page
        resp1 = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2025-10-01", "End": "2025-10-31"},
                    "Groups": [
                        {
                            "Keys": ["Amazon Elastic Compute Cloud - Compute"],
                            "Metrics": {"UnblendedCost": {"Amount": "12.50", "Unit": "USD"}},
                        }
                    ],
                }
            ],
            "NextPageToken": "token-1",
        }

        # Second (last) page
        resp2 = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2025-10-01", "End": "2025-10-31"},
                    "Groups": [
                        {
                            "Keys": ["Amazon RDS"],
                            "Metrics": {"UnblendedCost": {"Amount": "7.50", "Unit": "USD"}},
                        }
                    ],
                }
            ]
        }

        mock_client.get_cost_and_usage.side_effect = [resp1, resp2]
        # Configure the MagicMock Session to return a client with our mock_client
        boto3.Session.return_value.client.return_value = mock_client

        # Import and run under test
        from aws_resources.collectors.cost_explorer import CostExplorerCollector

        c = CostExplorerCollector()
        out = c.get_service_costs("2025-10-01", "2025-10-31")

        # Validate output contains both services
        services = {entry["service"]: entry for entry in out}
        self.assertIn("Amazon Elastic Compute Cloud - Compute", services)
        self.assertIn("Amazon RDS", services)
        self.assertEqual(services["Amazon Elastic Compute Cloud - Compute"]["amount"], 12.5)
        self.assertEqual(services["Amazon RDS"]["amount"], 7.5)


if __name__ == "__main__":
    unittest.main()
