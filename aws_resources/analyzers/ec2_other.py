import boto3
from typing import Dict, Any


class EC2OtherAnalyzer:
    """Analyzer for EC2 "other" resources (EBS volumes, snapshots).

    This is intentionally minimal: summary counts and sizes by default,
    and resource lists only when include_details=True. No CloudWatch or
    transfer aggregation is performed here.
    """

    def __init__(self, profile: str | None = None, region_name: str | None = None):
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.region_name = region_name

    def analyze(self, include_details: bool = False) -> Dict[str, Any]:
        ec2 = (
            self.session.client("ec2", region_name=self.region_name)
            if self.region_name
            else self.session.client("ec2")
        )

        vols_resp = ec2.describe_volumes()
        snaps_resp = ec2.describe_snapshots()

        volumes = vols_resp.get("Volumes", [])
        snapshots = snaps_resp.get("Snapshots", [])

        total_volumes = len(volumes)
        total_snapshots = len(snapshots)
        total_volume_gib = sum(v.get("Size", 0) for v in volumes)

        summary = {
            "total_volumes": total_volumes,
            "total_snapshots": total_snapshots,
            "total_volume_gib": total_volume_gib,
        }

        result: Dict[str, Any] = {"summary": summary}

        # always include the keys so callers can rely on consistent shape;
        # in summary mode they are empty lists, in details mode they contain
        # per-resource dictionaries.
        result["volumes"] = []
        result["snapshots"] = []

        if include_details:
            result["volumes"] = [
                {
                    "volume_id": v.get("VolumeId"),
                    "size_gib": v.get("Size"),
                    "state": v.get("State"),
                }
                for v in volumes
            ]
            result["snapshots"] = [
                {
                    "snapshot_id": s.get("SnapshotId"),
                    "volume_id": s.get("VolumeId"),
                    "size_gib": s.get("VolumeSize"),
                }
                for s in snapshots
            ]

        return result
