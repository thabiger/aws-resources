"""Lambda analyzer (module name `lambda`) — same implementation as previous
`lambda_analyzer.py`. We keep this file named `lambda.py` per user request, but
imports from this module must avoid the `from .lambda import ...` syntax which is
invalid (lambda is a Python keyword). Use importlib to import when needed.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import logging

try:
    import boto3
except Exception:  # pragma: no cover - tests inject a fake boto3
    boto3 = None  # type: ignore

logger = logging.getLogger(__name__)


class LambdaAnalyzer:
    def __init__(self, profile: Optional[str] = None, region_name: Optional[str] = None):
        self.profile = profile
        self.region_name = region_name
        if boto3 is None:
            raise RuntimeError("boto3 is required for LambdaAnalyzer")
        if profile:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()
        self.client = self.session.client("lambda", region_name=region_name)

    def analyze(self, include_details: bool = False) -> Dict[str, object]:
        functions: List[Dict] = []
        paginator = self.client.get_paginator("list_functions")

        total_memory = 0
        runtime_counts: Dict[str, int] = {}
        memory_buckets: Dict[int, int] = {}

        for page in paginator.paginate():
            for f in page.get("Functions", []):
                name = f.get("FunctionName")
                mem = f.get("MemorySize") or 0
                runtime = f.get("Runtime") or "unknown"
                handler = f.get("Handler")
                env = f.get("Environment", {}).get("Variables", {})

                functions.append({
                    "name": name,
                    "memory_mb": mem,
                    "runtime": runtime,
                    "handler": handler,
                })

                total_memory += mem
                runtime_counts[runtime] = runtime_counts.get(runtime, 0) + 1
                memory_buckets[mem] = memory_buckets.get(mem, 0) + 1

        result: Dict[str, object] = {
            "summary": {
                "total_functions": len(functions),
                "total_memory_mb": total_memory,
                "by_runtime": runtime_counts,
                "by_memory_mb": memory_buckets,
            },
        }

        if include_details:
            result["functions"] = functions

        return result
