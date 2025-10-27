import sys
import unittest
from unittest.mock import MagicMock, patch


class TestDocumentDBAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_documentdb_summary_and_details(self):
        import boto3

        mock_docdb = MagicMock()
        # clusters: one cluster 'c1'
        mock_docdb.get_paginator.return_value.paginate.return_value = [
            {"DBClusters": [{"DBClusterIdentifier": "c1", "Engine": "docdb", "Status": "available"}]}
        ]

        # describe_db_instances paginator: two instances in cluster c1
        def paginate_instances():
            return [{"DBInstances": [
                {"DBInstanceIdentifier": "i-1", "DBInstanceClass": "db.r5.large", "DBClusterIdentifier": "c1", "Endpoint": {"Address": "i-1.example.com"}, "DBInstanceStatus": "available"},
                {"DBInstanceIdentifier": "i-2", "DBInstanceClass": "db.r5.large", "DBClusterIdentifier": "c1", "Endpoint": {"Address": "i-2.example.com"}, "DBInstanceStatus": "available"},
            ]}]

        # make paginate behave differently by caller: we'll intercept in tests by swapping client
        # configure describe_db_instances to return the two instances
        mock_docdb.get_paginator.side_effect = lambda op: MagicMock(paginate=lambda: paginate_instances()) if op == "describe_db_instances" else MagicMock(paginate=lambda: [{"DBClusters": [{"DBClusterIdentifier": "c1", "Engine": "docdb", "Status": "available"}]}])

        # mock ec2 describe_instance_types
        mock_ec2 = MagicMock()
        mock_ec2.describe_instance_types.return_value = {
            "InstanceTypes": [
                {"InstanceType": "r5.large", "VCpuInfo": {"DefaultVCpus": 2}, "MemoryInfo": {"SizeInMiB": 16384}},
            ]
        }

        def client_factory(name, region_name=None):
            if name == "docdb":
                return mock_docdb
            if name == "ec2":
                return mock_ec2
            return MagicMock()

        boto3.Session.return_value.client.side_effect = client_factory

        from aws_resources.analyzers.documentdb import DocumentDBAnalyzer

        a = DocumentDBAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_clusters"], 1)
        # instances are discovered via describe_db_instances even in summary
        self.assertEqual(out["summary"]["total_nodes"], 2)

        out2 = a.analyze(include_details=True)
        self.assertIn("clusters", out2)
        self.assertEqual(len(out2["clusters"]), 1)
        self.assertIn("by_instance_type", out2["summary"])
        self.assertEqual(out2["summary"]["total_vCPU"], 4)


if __name__ == "__main__":
    unittest.main()
