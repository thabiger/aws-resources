import sys
import unittest
from unittest.mock import MagicMock, patch


class TestSESAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_ses_summary_and_details(self):
        import boto3

        mock_client = MagicMock()
        # first call (EmailAddress) returns the email identity, second (Domain) returns empty
        # Provide responses for two calls per analyze invocation (EmailAddress, Domain).
        # The test calls analyze() twice, so provide four items.
        mock_client.list_identities.side_effect = [
            {"Identities": ["user@example.com"]},
            {"Identities": []},
            {"Identities": ["user@example.com"]},
            {"Identities": []},
        ]
        mock_client.get_identity_verification_attributes.return_value = {"VerificationAttributes": {"user@example.com": {"VerificationStatus": "Success"}}}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.ses import SESAnalyzer

        a = SESAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_identities"], 1)

        out2 = a.analyze(include_details=True)
        self.assertIn("identities", out2)
        self.assertEqual(out2["identities"][0]["verification_status"], "Success")


if __name__ == "__main__":
    unittest.main()
