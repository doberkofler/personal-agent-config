"""Shared release tag format for the maintainer command and CI builder."""
from __future__ import annotations

import re
from collections.abc import Iterable

STABLE_VERSION_FORMAT = r"v([0-9]+)\.([0-9]+)\.([0-9]+)"
STABLE_VERSION_PATTERN = re.compile(STABLE_VERSION_FORMAT)
VERSION_PATTERN = re.compile(rf"{STABLE_VERSION_FORMAT}(?:[-+][0-9A-Za-z.-]+)?")


def is_release_version(version: str) -> bool:
    return VERSION_PATTERN.fullmatch(version) is not None


def suggest_version(tags: Iterable[str]) -> tuple[str | None, str]:
    """Return the highest plain version tag and the next patch version."""
    latest: tuple[int, int, int, str] | None = None
    for tag in tags:
        match = STABLE_VERSION_PATTERN.fullmatch(tag)
        if match is None:
            continue
        major, minor, patch = match.groups()
        candidate = (int(major), int(minor), int(patch), tag)
        if latest is None or candidate > latest:
            latest = candidate

    if latest is None:
        return None, "v1.0.0"
    major_number, minor_number, patch_number, tag = latest
    return tag, f"v{major_number}.{minor_number}.{patch_number + 1}"
