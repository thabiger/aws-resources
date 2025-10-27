import sys
import unittest
from unittest.mock import MagicMock, patch


class TestCloudFrontAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_cloudfront_analyze_summary_and_details(self):
        import boto3

        mock_client = MagicMock()

        mock_client.get_paginator.return_value.paginate.return_value = [
            {
                "DistributionList": {
                    "Items": [
                        {
                            "Id": "EDFDVBD6EXAMPLE",
                            "DomainName": "d111111abcdef8.cloudfront.net",
                            "Enabled": True,
                            "Origins": {"Items": [{"Id": "origin1"}]},
                            "Aliases": {"Items": []},
                            "Comment": "",
                        },
                        {
                            "Id": "EXAMPLE2",
                            "DomainName": "d22222.cloudfront.net",
                            "Enabled": False,
                            "Origins": {"Items": [{"Id": "originA"}, {"Id": "originB"}]},
                            "Aliases": {"Items": [{"CNAME": "example.com"}]},
                            "Comment": "test",
                        },
                    ]
                }
            }
        ]

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.cloudfront import CloudFrontAnalyzer

        a = CloudFrontAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_distributions"], 2)
        self.assertEqual(out["summary"]["enabled"], 1)
        self.assertEqual(out["summary"]["disabled"], 1)

        out2 = a.analyze(include_details=True)
        self.assertIn("distributions", out2)
        self.assertEqual(len(out2["distributions"]), 2)
        self.assertEqual(out2["distributions"][0]["id"], "EDFDVBD6EXAMPLE")


if __name__ == "__main__":
    unittest.main()
