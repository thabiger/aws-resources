import sys
import unittest
from unittest.mock import MagicMock, patch


class TestSQSAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_sqs_summary_and_details(self):
        import boto3

        mock_client = MagicMock()
        mock_client.list_queues.return_value = {"QueueUrls": ["https://sqs.us-east-1.amazonaws.com/123/queue1"]}
        mock_client.get_queue_attributes.return_value = {"Attributes": {"ApproximateNumberOfMessages": "5"}}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.sqs import SQSAnalyzer

        a = SQSAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_queues"], 1)

        out2 = a.analyze(include_details=True)
        self.assertIn("queues", out2)
        self.assertEqual(out2["queues"][0]["attributes"]["ApproximateNumberOfMessages"], "5")


if __name__ == "__main__":
    unittest.main()
