"""VPC analyzer

Collects information about VPCs and related resources (subnets, NAT gateways,
internet gateways, route tables, VPC endpoints, security groups). This is a
best-effort inventory useful for understanding networking footprint.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:  # pragma: no cover - tests will inject a fake boto3
    boto3 = None  # type: ignore

logger = logging.getLogger(__name__)


class VPCAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for VPCAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("ec2", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        """Return VPC inventory and summary.

        Output example:
        {
            "vpcs": [{"vpc_id": "vpc-...", "is_default": False, "cidr_block": "10.0.0.0/16", "subnet_count": 3, ...}],
            "summary": {"total_vpcs": 2, "total_subnets": 6, "total_nat_gateways": 1, ...}
        }
        """
        vpc_resp = self.client.describe_vpcs()
        vpcs = vpc_resp.get("Vpcs", [])

        out_vpcs: List[Dict] = []
        total_subnets = 0
        total_nat = 0
        total_igw = 0
        total_route_tables = 0
        total_endpoints = 0
        total_security_groups = 0

        for v in vpcs:
            vpc_id = v.get("VpcId")
            cidr = v.get("CidrBlock")
            is_default = v.get("IsDefault")
            state = v.get("State")
            tags = {t.get("Key"): t.get("Value") for t in (v.get("Tags") or [])}

            # subnets
            subnets = self.client.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
            s_count = len(subnets.get("Subnets", []))

            # NAT gateways
            nat = self.client.describe_nat_gateways(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
            nat_count = len(nat.get("NatGateways", []))

            # Internet gateways attached
            igws = self.client.describe_internet_gateways(Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}])
            igw_count = len(igws.get("InternetGateways", []))

            # route tables
            rts = self.client.describe_route_tables(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
            rt_count = len(rts.get("RouteTables", []))

            # vpc endpoints
            eps = self.client.describe_vpc_endpoints(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
            ep_count = len(eps.get("VpcEndpoints", []))

            # security groups
            sgs = self.client.describe_security_groups(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
            sg_count = len(sgs.get("SecurityGroups", []))

            out_vpcs.append({
                "vpc_id": vpc_id,
                "is_default": bool(is_default),
                "cidr_block": cidr,
                "state": state,
                "tags": tags,
                "subnet_count": s_count,
                "nat_gateway_count": nat_count,
                "internet_gateway_count": igw_count,
                "route_table_count": rt_count,
                "vpc_endpoint_count": ep_count,
                "security_group_count": sg_count,
            })

            total_subnets += s_count
            total_nat += nat_count
            total_igw += igw_count
            total_route_tables += rt_count
            total_endpoints += ep_count
            total_security_groups += sg_count

        summary = {
            "total_vpcs": len(out_vpcs),
            "total_subnets": total_subnets,
            "total_nat_gateways": total_nat,
            "total_internet_gateways": total_igw,
            "total_route_tables": total_route_tables,
            "total_vpc_endpoints": total_endpoints,
            "total_security_groups": total_security_groups,
        }

        result: Dict[str, object] = {"summary": summary}

        if include_details:
            result["vpcs"] = out_vpcs

        return result
