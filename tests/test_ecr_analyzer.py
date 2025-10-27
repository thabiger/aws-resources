import sys
import unittest
from unittest.mock import MagicMock, patch


class TestECRAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_ecr_summary_and_details(self):
        import boto3

        mock_client = MagicMock()
        mock_client.get_paginator.return_value.paginate.return_value = [
            {"repositories": [{"repositoryName": "repo1", "repositoryUri": "uri1"}, {"repositoryName": "repo2", "repositoryUri": "uri2"}]}
        ]

        mock_client.list_images.return_value = {"imageIds": [{}, {}, {}]}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.ecr import ECRAnalyzer

        a = ECRAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_repositories"], 2)

        out2 = a.analyze(include_details=True)
        self.assertIn("repositories", out2)
        self.assertEqual(len(out2["repositories"]), 2)
        self.assertEqual(out2["repositories"][0]["image_count"], 3)


if __name__ == "__main__":
    unittest.main()
