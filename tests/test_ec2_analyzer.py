import sys
import unittest
from unittest.mock import MagicMock, patch


class TestEC2Analyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_analyze_instances(self):
        import boto3

        # Prepare mocked client behavior
        mock_client = MagicMock()

        # describe_instances paginator
        mock_client.get_paginator.return_value.paginate.return_value = [
            {
                "Reservations": [
                    {
                        "Instances": [
                            {
                                "InstanceId": "i-1",
                                "InstanceType": "t3.micro",
                                "State": {"Name": "running"},
                                "Architecture": "x86_64",
                            },
                            {
                                "InstanceId": "i-2",
                                "InstanceType": "t3.medium",
                                "State": {"Name": "stopped"},
                                "Architecture": "arm64",
                            },
                        ]
                    }
                ]
            }
        ]

        # describe_instance_types response
        mock_client.describe_instance_types.return_value = {
            "InstanceTypes": [
                {
                    "InstanceType": "t3.micro",
                    "VCpuInfo": {"DefaultVCpus": 2},
                    "MemoryInfo": {"SizeInMiB": 1024},
                    "ProcessorInfo": {"SupportedArchitectures": ["x86_64"]},
                },
                {
                    "InstanceType": "t3.medium",
                    "VCpuInfo": {"DefaultVCpus": 2},
                    "MemoryInfo": {"SizeInMiB": 4096},
                    "ProcessorInfo": {"SupportedArchitectures": ["x86_64"]},
                },
            ]
        }

        boto3.Session.return_value.client.return_value = mock_client

    from aws_resources.analyzers.ec2 import EC2Analyzer

    a = EC2Analyzer()
    out = a.analyze()

    self.assertEqual(out["summary"]["total_instances"], 2)
    self.assertEqual(out["summary"]["total_vCPU"], 4)
    self.assertEqual(out["summary"]["total_memory_mib"], 1024 + 4096)
    # architecture breakdown
    arch = out["summary"].get("architecture", {})
    self.assertEqual(arch.get("x86", {}).get("count"), 1)
    self.assertEqual(arch.get("arm", {}).get("count"), 1)
    self.assertEqual(arch.get("x86", {}).get("vCPU"), 2)
    self.assertEqual(arch.get("arm", {}).get("vCPU"), 2)
    # lifecycle-by-architecture
    lba = out["summary"].get("lifecycle_by_architecture", {})
    self.assertEqual(lba.get("x86", {}).get("on_demand_count"), 1)
    self.assertEqual(lba.get("arm", {}).get("on_demand_count"), 1)
    # lifecycle: both default to on_demand in this test
    self.assertEqual(out["summary"]["total_spot"], 0)
    self.assertEqual(out["summary"]["total_on_demand"], 2)
    self.assertEqual(out["summary"]["spot_vCPU"], 0)
    self.assertEqual(out["summary"]["spot_memory_mib"], 0)
    self.assertEqual(out["summary"]["on_demand_vCPU"], 4)
    self.assertEqual(out["summary"]["on_demand_memory_mib"], 1024 + 4096)


if __name__ == "__main__":
    unittest.main()
