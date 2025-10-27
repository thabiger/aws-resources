import sys
import unittest
from unittest.mock import MagicMock, patch


class TestSNSAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_sns_summary_and_details(self):
        import boto3

        mock_client = MagicMock()
        mock_client.get_paginator.return_value.paginate.return_value = [{"Topics": [{"TopicArn": "arn:topic:1"}, {"TopicArn": "arn:topic:2"}]}]
        mock_client.get_topic_attributes.return_value = {"Attributes": {"DisplayName": "t1"}}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.sns import SNSAnalyzer

        a = SNSAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_topics"], 2)

        out2 = a.analyze(include_details=True)
        self.assertIn("topics", out2)
        self.assertEqual(out2["topics"][0]["attributes"]["DisplayName"], "t1")


if __name__ == "__main__":
    unittest.main()
