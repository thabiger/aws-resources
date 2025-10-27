from __future__ import annotations

from typing import Any, Dict


class Analyzer:
    """Base class for service analyzers.

    Implementations should provide an `analyze()` method which returns a structured dict
    with details and a summary, or raise an exception on unrecoverable errors.
    """
    def analyze(self, include_details: bool = False) -> Dict[str, Any]:
        """Run analysis.

        Args:
            include_details: when True, return resource-level details in addition to summary.
        Returns:
            A structured dict with analyzer results.
        """
        raise NotImplementedError()
