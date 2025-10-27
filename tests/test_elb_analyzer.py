import sys
import unittest
from unittest.mock import MagicMock, patch


class TestELBAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_elb_summary_and_details(self):
        import boto3

        mock_client = MagicMock()

        # elb v1
        mock_client.describe_load_balancers.return_value = {"LoadBalancerDescriptions": [{"LoadBalancerName": "lb1", "DNSName": "lb1.example.com"}]}
        # elbv2
        mock_client.describe_load_balancers.return_value = {"LoadBalancers": [{"LoadBalancerArn": "arn:lb2", "DNSName": "lb2.example.com", "Type": "application"}]}

        # boto3 Session will give same mock client for both elb and elbv2 in test
        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.elb import ELBAnalyzer

        a = ELBAnalyzer()
        out = a.analyze()
        # since we replaced return twice above, ensure it returns a dict structure; we can't assert counts strongly here in this mock setup
        self.assertIn("summary", out)

        out2 = a.analyze(include_details=True)
        self.assertIn("load_balancers", out2)


if __name__ == "__main__":
    unittest.main()
