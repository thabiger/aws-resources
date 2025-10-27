import sys
import unittest
from unittest.mock import MagicMock, patch


class TestVPCAnalyzer(unittest.TestCase):
    @patch.dict(sys.modules, {"boto3": MagicMock()})
    def test_vpc_analyze(self):
        import boto3

        mock_client = MagicMock()

        # describe_vpcs
        mock_client.describe_vpcs.return_value = {
            "Vpcs": [
                {"VpcId": "vpc-1", "CidrBlock": "10.0.0.0/16", "IsDefault": False, "State": "available", "Tags": [{"Key": "Name", "Value": "prod"}]}
            ]
        }

        # describe_subnets
        mock_client.describe_subnets.return_value = {"Subnets": [{}, {}]}
        # describe_nat_gateways
        mock_client.describe_nat_gateways.return_value = {"NatGateways": [{}]}
        # describe_internet_gateways
        mock_client.describe_internet_gateways.return_value = {"InternetGateways": [{}]}
        # describe_route_tables
        mock_client.describe_route_tables.return_value = {"RouteTables": [{}, {}]}
        # describe_vpc_endpoints
        mock_client.describe_vpc_endpoints.return_value = {"VpcEndpoints": []}
        # describe_security_groups
        mock_client.describe_security_groups.return_value = {"SecurityGroups": [{}, {}]}

        boto3.Session.return_value.client.return_value = mock_client

        from aws_resources.analyzers.vpc import VPCAnalyzer

        a = VPCAnalyzer()
        out = a.analyze()

        self.assertEqual(out["summary"]["total_vpcs"], 1)
        self.assertEqual(out["summary"]["total_subnets"], 2)
        self.assertEqual(out["summary"]["total_nat_gateways"], 1)
        self.assertEqual(out["summary"]["total_internet_gateways"], 1)
        self.assertEqual(out["vpcs"][0]["tags"]["Name"], "prod")


if __name__ == "__main__":
    unittest.main()
