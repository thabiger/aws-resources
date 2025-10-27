import sys
import unittest
from unittest.mock import MagicMock, patch


class TestRoute53Analyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_route53_summary_and_details(self):
        import boto3

        mock_client = MagicMock()
        mock_client.list_hosted_zones.return_value = {"HostedZones": [{"Id": "Z1", "Name": "example.com.", "Config": {"PrivateZone": False}}]}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.route53 import Route53Analyzer

        a = Route53Analyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_hosted_zones"], 1)
        # breakdown by type: public vs private
        self.assertIn("by_type", out["summary"])
        self.assertEqual(out["summary"]["by_type"]["public"], 1)
        self.assertEqual(out["summary"]["by_type"]["private"], 0)

        out2 = a.analyze(include_details=True)
        self.assertIn("hosted_zones", out2)
        self.assertEqual(out2["hosted_zones"][0]["name"], "example.com.")


if __name__ == "__main__":
    unittest.main()
