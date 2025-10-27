import sys
import unittest
from unittest.mock import MagicMock, patch


class TestKMSAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_kms_summary_and_details(self):
        import boto3

        mock_client = MagicMock()
        mock_client.get_paginator.return_value.paginate.return_value = [{"Keys": [{"KeyId": "key-1"}, {"KeyId": "key-2"}]}]
        mock_client.describe_key.side_effect = lambda KeyId=None: {"KeyMetadata": {"Description": f"desc-{KeyId}", "KeyState": "Enabled"}}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.kms import KMSAnalyzer

        a = KMSAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_keys"], 2)

        out2 = a.analyze(include_details=True)
        self.assertIn("keys", out2)
        self.assertEqual(out2["keys"][0]["key_state"], "Enabled")


if __name__ == "__main__":
    unittest.main()
