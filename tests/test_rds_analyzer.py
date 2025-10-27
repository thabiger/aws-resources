import sys
import unittest
from unittest.mock import MagicMock, patch


class TestRDSAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_rds_analyze(self):
        import boto3

        mock_client = MagicMock()

        # Paginator returns one page with two DB instances
        mock_client.get_paginator.return_value.paginate.return_value = [
            {
                "DBInstances": [
                    {
                        "DBInstanceIdentifier": "db-1",
                        "DBInstanceClass": "db.t3.micro",
                        "Engine": "postgres",
                        "DBInstanceStatus": "available",
                        "MultiAZ": False,
                        "AllocatedStorage": 20,
                        "Endpoint": {"Address": "db-1.example.com"},
                    },
                    {
                        "DBInstanceIdentifier": "db-2",
                        "DBInstanceClass": "db.t3.medium",
                        "Engine": "mysql",
                        "DBInstanceStatus": "available",
                        "MultiAZ": True,
                        "AllocatedStorage": 100,
                        "Endpoint": {"Address": "db-2.example.com"},
                    },
                ]
            }
        ]

        # For this test, the same mock_client will be used for both rds and ec2
        # clients; provide describe_instance_types response as well.
        mock_client.describe_instance_types.return_value = {
            "InstanceTypes": [
                {"InstanceType": "t3.micro", "VCpuInfo": {"DefaultVCpus": 2}, "MemoryInfo": {"SizeInMiB": 1024}},
                {"InstanceType": "t3.medium", "VCpuInfo": {"DefaultVCpus": 2}, "MemoryInfo": {"SizeInMiB": 4096}},
            ]
        }

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.rds import RDSAnalyzer

        a = RDSAnalyzer()
        out = a.analyze()

        self.assertEqual(out["summary"]["total_instances"], 2)
        self.assertEqual(out["summary"]["total_allocated_storage_gib"], 120)
        # vCPU mapping present in STATIC_RDS_CLASS_MAP for our test classes
        self.assertEqual(out["summary"]["total_vCPU"], 2 + 2)
        self.assertTrue("postgres" in out["summary"]["by_engine"])
        self.assertTrue("db.t3.micro" in out["summary"]["by_class"])

        # verify include_details returns instance list
        out_details = a.analyze(include_details=True)
        self.assertIn("instances", out_details)
        self.assertEqual(len(out_details["instances"]), 2)
        self.assertEqual(out_details["instances"][0]["id"], "db-1")


if __name__ == "__main__":
    unittest.main()
