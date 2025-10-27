import sys
import unittest
from unittest.mock import MagicMock, patch


class TestS3Analyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_s3_analyze_summary_and_details(self):
        import boto3

        mock_client = MagicMock()

        mock_client.list_buckets.return_value = {
            "Buckets": [
                {"Name": "bucket-1", "CreationDate": "2020-01-01"},
                {"Name": "bucket-2", "CreationDate": "2021-01-01"},
            ]
        }

        # get_bucket_location should be called when include_details is True
        mock_client.get_bucket_location.return_value = {"LocationConstraint": "us-west-2"}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.s3 import S3Analyzer

        # default summary-only
        a = S3Analyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_buckets"], 2)

        # with details
        a2 = S3Analyzer()
        out2 = a2.analyze(include_details=True)
        self.assertEqual(out2["summary"]["total_buckets"], 2)
        self.assertIn("buckets", out2)
        self.assertEqual(len(out2["buckets"]), 2)
        self.assertEqual(out2["buckets"][0]["name"], "bucket-1")


if __name__ == "__main__":
    unittest.main()
