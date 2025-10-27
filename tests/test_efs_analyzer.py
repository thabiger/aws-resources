import sys
import unittest
from unittest.mock import MagicMock, patch


class TestEFSAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_efs_summary_and_details(self):
        import boto3

        mock_client = MagicMock()
        mock_client.describe_file_systems.return_value = {"FileSystems": [{"FileSystemId": "fs-1", "CreationTime": "2023-01-01", "SizeInBytes": {"Value": 1024}, "ThroughputMode": "bursting"}]}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.efs import EFSAnalyzer

        a = EFSAnalyzer()
        out = a.analyze()
        self.assertEqual(out["summary"]["total_file_systems"], 1)
        # summarized by throughput mode
        self.assertIn("by_throughput_mode", out["summary"])
        self.assertIn("bursting", out["summary"]["by_throughput_mode"])
        self.assertEqual(out["summary"]["by_throughput_mode"]["bursting"]["count"], 1)
        self.assertEqual(out["summary"]["by_throughput_mode"]["bursting"]["total_size_bytes"], 1024)

        out2 = a.analyze(include_details=True)
        self.assertIn("file_systems", out2)
        self.assertEqual(out2["file_systems"][0]["file_system_id"], "fs-1")


if __name__ == "__main__":
    unittest.main()
