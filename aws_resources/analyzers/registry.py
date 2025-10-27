"""Registry for analyzers mapping Cost Explorer service names to analyzer classes"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Type

_REGISTRY: Dict[str, Callable[[], object]] = {}


def register_analyzer(service_token: str, factory: Callable[[], object]) -> None:
    """Register an analyzer factory for a service token.

    The service_token should match the Cost Explorer 'SERVICE' Key used in grouping.
    Example: 'Amazon Elastic Compute Cloud - Compute'
    """
    _REGISTRY[service_token.lower()] = factory


def get_analyzer_for_service(service_token: str) -> Optional[object]:
    return _REGISTRY.get(service_token.lower(), None)
