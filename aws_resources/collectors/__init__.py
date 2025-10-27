"""Collectors package for aws_resources

This module intentionally avoids importing submodules at import-time to prevent
hard failures when optional runtime dependencies (like boto3) are not present
during test discovery. Import the concrete collectors directly when needed.
"""

__all__ = []
