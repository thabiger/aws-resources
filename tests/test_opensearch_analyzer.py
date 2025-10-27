import sys
import unittest
from unittest.mock import MagicMock, patch


class TestOpenSearchAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_opensearch_summary_and_details(self):
        import boto3

        # mock opensearch client responses
        mock_os = MagicMock()
        mock_os.list_domain_names.return_value = {"DomainNames": [{"DomainName": "d1"}, {"DomainName": "d2"}]}
        # d1 has 2 m5.large.search nodes, d2 has 1 r5.large.search node
        d1_status = {
            "DomainName": "d1",
            "Created": True,
            "Endpoint": "d1.example.com",
            "ClusterConfig": {"InstanceType": "m5.large.search", "InstanceCount": 2},
        }
        d2_status = {
            "DomainName": "d2",
            "Created": True,
            "Endpoint": "d2.example.com",
            "ClusterConfig": {"InstanceType": "r5.large.search", "InstanceCount": 1},
        }

        def describe_domains_side_effect(DomainNames=None):
            if DomainNames and DomainNames[0] == "d1":
                return {"DomainStatusList": [d1_status]}
            if DomainNames and DomainNames[0] == "d2":
                return {"DomainStatusList": [d2_status]}
            return {"DomainStatusList": []}

        mock_os.describe_domains.side_effect = describe_domains_side_effect

        # mock ec2 client for describe_instance_types
        mock_ec2 = MagicMock()
        mock_ec2.describe_instance_types.return_value = {
            "InstanceTypes": [
                {"InstanceType": "m5.large", "VCpuInfo": {"DefaultVCpus": 2}, "MemoryInfo": {"SizeInMiB": 8192}},
                {"InstanceType": "r5.large", "VCpuInfo": {"DefaultVCpus": 2}, "MemoryInfo": {"SizeInMiB": 16384}},
            ]
        }

        def client_factory(name, region_name=None):
            if name in ("opensearch", "es"):
                return mock_os
            if name == "ec2":
                return mock_ec2
            return MagicMock()

        boto3.Session.return_value.client.side_effect = client_factory

        from aws_resources.analyzers.opensearch import OpenSearchAnalyzer

        a = OpenSearchAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_domains"], 2)
        # nodes and totals computed
        self.assertEqual(out["summary"]["total_nodes"], 3)
        self.assertEqual(out["summary"]["total_vCPU"], 2 * 2 + 2 * 1)
        self.assertEqual(out["summary"]["total_memory_mib"], 8192 * 2 + 16384 * 1)

        out2 = a.analyze(include_details=True)
        self.assertIn("domains", out2)
        self.assertEqual(out2["domains"][0]["endpoint"], "d1.example.com")


if __name__ == "__main__":
    unittest.main()
