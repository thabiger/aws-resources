import sys
import unittest
from unittest.mock import MagicMock, patch


class TestElastiCacheAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_elasticache_summary_and_details(self):
        import boto3

        # mock elasticache paginator: two clusters with explicit CacheNodeType
        mock_ec = MagicMock()
        mock_ec.get_paginator.return_value.paginate.return_value = [
            {
                "CacheClusters": [
                    {"CacheClusterId": "cc1", "Engine": "redis", "NumCacheNodes": 2, "CacheClusterStatus": "available", "CacheNodeType": "cache.m5.large"},
                    {"CacheClusterId": "cc2", "Engine": "memcached", "NumCacheNodes": 1, "CacheClusterStatus": "available", "CacheNodeType": "cache.r5.large"},
                ]
            }
        ]

        # mock ec2 describe_instance_types
        mock_ec2 = MagicMock()
        mock_ec2.describe_instance_types.return_value = {
            "InstanceTypes": [
                {"InstanceType": "m5.large", "VCpuInfo": {"DefaultVCpus": 2}, "MemoryInfo": {"SizeInMiB": 8192}},
                {"InstanceType": "r5.large", "VCpuInfo": {"DefaultVCpus": 2}, "MemoryInfo": {"SizeInMiB": 16384}},
            ]
        }

        def client_factory(name, region_name=None):
            if name == "elasticache":
                return mock_ec
            if name == "ec2":
                return mock_ec2
            return MagicMock()

        boto3.Session.return_value.client.side_effect = client_factory

        from aws_resources.analyzers.elasticache import ElastiCacheAnalyzer

        a = ElastiCacheAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_clusters"], 2)
        self.assertEqual(out["summary"]["total_nodes"], 3)
        # vCPU: cc1 has 2 * 2, cc2 has 1 * 2 => total 6
        self.assertEqual(out["summary"]["total_vCPU"], 6)
        # memory: 2 * 8192 + 1 * 16384
        self.assertEqual(out["summary"]["total_memory_mib"], 8192 * 2 + 16384 * 1)

        out2 = a.analyze(include_details=True)
        self.assertIn("clusters", out2)
        self.assertEqual(out2["clusters"][0]["cache_cluster_id"], "cc1")


if __name__ == "__main__":
    unittest.main()
