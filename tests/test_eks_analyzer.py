import sys
import unittest
from unittest.mock import MagicMock, patch


class TestEKSAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_eks_summary_and_details(self):
        import boto3

        mock_client = MagicMock()
        mock_client.get_paginator.return_value.paginate.return_value = [
            {"clusters": ["cluster-a", "cluster-b"]}
        ]

        mock_client.describe_cluster.side_effect = lambda name: {"cluster": {"name": name, "status": "ACTIVE", "version": "1.27"}}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.eks import EKSAnalyzer

        a = EKSAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_clusters"], 2)

        out2 = a.analyze(include_details=True)
        self.assertIn("clusters", out2)
        self.assertEqual(out2["clusters"][0]["version"], "1.27")


if __name__ == "__main__":
    unittest.main()
