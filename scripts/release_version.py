"""Shared release tag format for the maintainer command and CI builder."""
from __future__ import annotations

import re

VERSION_PATTERN = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?")


def is_release_version(version: str) -> bool:
    return VERSION_PATTERN.fullmatch(version) is not None
