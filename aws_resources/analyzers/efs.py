"""EFS analyzer

Summarizes EFS file systems. Optional details include per-filesystem size/mount targets.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:
    boto3 = None

logger = logging.getLogger(__name__)


class EFSAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for EFSAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("efs", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        resp = self.client.describe_file_systems()
        fss = resp.get("FileSystems", [])
        total = len(fss)

        # summarize sizes/counts by throughput mode for non-detailed summary
        by_throughput: Dict[str, Dict[str, int]] = {}
        for fs in fss:
            mode = fs.get("ThroughputMode") or "unknown"
            size = (fs.get("SizeInBytes") or {}).get("Value") or 0
            if mode not in by_throughput:
                by_throughput[mode] = {"count": 0, "total_size_bytes": 0}
            by_throughput[mode]["count"] += 1
            by_throughput[mode]["total_size_bytes"] += size

        result = {"summary": {"total_file_systems": total, "by_throughput_mode": by_throughput}}

        if include_details:
            details = []
            for fs in fss:
                details.append({
                    "file_system_id": fs.get("FileSystemId"),
                    "creation_time": str(fs.get("CreationTime")),
                    "size_bytes": fs.get("SizeInBytes", {}).get("Value"),
                    "throughput_mode": fs.get("ThroughputMode"),
                })
            result["file_systems"] = details

        return result
