
import sys
import unittest
from unittest.mock import MagicMock, patch


class TestEC2OtherAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_ec2_other_analyze(self):
        import boto3

        mock_ec2 = MagicMock()
        mock_ec2.describe_volumes.return_value = {"Volumes": [{"VolumeId": "vol-1", "Size": 8, "State": "available"}]}
        mock_ec2.describe_snapshots.return_value = {"Snapshots": [{"SnapshotId": "snap-1", "VolumeId": "vol-1", "VolumeSize": 8}]}

        boto3.Session.return_value.client.return_value = mock_ec2

        from aws_resources.analyzers.ec2_other import EC2OtherAnalyzer

        a = EC2OtherAnalyzer()
        out = a.analyze()

        self.assertIn("volumes", out)
        self.assertIn("snapshots", out)

        # verify include_details returns volumes/snapshots
        out2 = a.analyze(include_details=True)
        self.assertIn("volumes", out2)
        self.assertIn("snapshots", out2)
        self.assertEqual(out2["volumes"][0]["volume_id"], "vol-1")


if __name__ == "__main__":
    unittest.main()

