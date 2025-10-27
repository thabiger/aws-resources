import sys
import unittest
from unittest.mock import MagicMock, patch


class TestECSAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_ecs_summary_and_details(self):
        import boto3

        mock_client = MagicMock()
        mock_client.get_paginator.return_value.paginate.return_value = [
            {"clusterArns": ["arn:aws:ecs:us-east-1:123:cluster/clusterA"]}
        ]

        mock_client.describe_clusters.return_value = {"clusters": [{"clusterName": "clusterA", "status": "ACTIVE"}]}
        mock_client.list_services.return_value = {"serviceArns": ["s1", "s2"]}
        mock_client.list_tasks.return_value = {"taskArns": ["t1"]}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.ecs import ECSAnalyzer

        a = ECSAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_clusters"], 1)

        out2 = a.analyze(include_details=True)
        self.assertIn("clusters", out2)
        self.assertEqual(out2["clusters"][0]["service_count"], 2)
        self.assertEqual(out2["clusters"][0]["task_count"], 1)


if __name__ == "__main__":
    unittest.main()
