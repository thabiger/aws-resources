import sys
import unittest
from unittest.mock import MagicMock, patch


class TestDirectConnectAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_directconnect_summary_and_details(self):
        import boto3

        mock_client = MagicMock()
        mock_client.describe_connections.return_value = {"connections": [{"connectionId": "dxcon-1", "location": "EqDC2", "bandwidth": "1Gbps", "connectionState": "available"}]}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.directconnect import DirectConnectAnalyzer

        a = DirectConnectAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_connections"], 1)

        out2 = a.analyze(include_details=True)
        self.assertIn("connections", out2)
        self.assertEqual(out2["connections"][0]["connectionId"], "dxcon-1")


if __name__ == "__main__":
    unittest.main()
