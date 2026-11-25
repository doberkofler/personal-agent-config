#!/usr/bin/env python3
"""Cut a release by pushing one confirmed annotated tag to origin."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from scripts.release_version import is_release_version

REPO_ROOT = Path(__file__).resolve().parent
MAIN_REF = "refs/heads/main"


class ReleaseError(Exception):
    """A release preflight or Git operation failed."""


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        details = result.stderr.strip() or f"exit status {result.returncode}"
        raise ReleaseError(f"git {args[0]} failed: {details}")
    return result.stdout.strip()


def validate_version(version: str) -> str:
    if not is_release_version(version):
        raise ReleaseError(f"Invalid version {version!r}; expected a tag like v1.2.3.")
    tag_ref = f"refs/tags/{version}"
    try:
        git("check-ref-format", tag_ref)
    except ReleaseError as error:
        raise ReleaseError(f"Invalid version {version!r}; not a valid Git tag.") from error
    return tag_ref


def release_candidate(version: str, tag_ref: str) -> str:
    if git("branch", "--show-current") != "main":
        raise ReleaseError("Run this from the main branch.")
    if git("status", "--porcelain", "--untracked-files=all"):
        raise ReleaseError("Release requires a clean working tree.")
    if git("tag", "--list", version):
        raise ReleaseError(f"Tag {version} already exists locally.")

    commit = git("rev-parse", "--verify", "HEAD")
    # Read origin directly; the local tracking ref may be stale.
    remote_refs: dict[str, str] = {}
    for line in git("ls-remote", "--refs", "origin", MAIN_REF, tag_ref).splitlines():
        object_id, ref = line.split("\t", 1)
        remote_refs[ref] = object_id
    if tag_ref in remote_refs:
        raise ReleaseError(f"Tag {version} already exists on origin.")
    if MAIN_REF not in remote_refs:
        raise ReleaseError("origin/main is missing.")
    if remote_refs[MAIN_REF] != commit:
        raise ReleaseError("Local main does not match origin/main. Sync it before releasing.")
    return commit


def cut_release() -> None:
    version = input("Release version (e.g. v1.2.3): ").strip()
    tag_ref = validate_version(version)
    commit = release_candidate(version, tag_ref)
    print(f"{version} -> {commit} (origin/main)")
    confirmation = input("Create and push this tag to origin? [y/N] ").strip().lower()
    if confirmation not in {"y", "yes"}:
        print("Cancelled. No tag was created.")
        return

    if release_candidate(version, tag_ref) != commit:
        raise ReleaseError("The release candidate changed. Run the command again.")
    git("tag", "--annotate", "--message", f"Release {version}", version, commit)
    try:
        git("push", "--no-follow-tags", "origin", tag_ref)
    except (ReleaseError, OSError) as error:
        raise ReleaseError(
            f"{error}\nLocal tag {version} was kept. Check origin before retrying the push."
        ) from error
    print(f"Pushed {version}. The GitHub Actions release workflow now builds and publishes it.")


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        cut_release()
    except (ReleaseError, OSError) as error:
        print(f"Release stopped: {error}", file=sys.stderr)
        return 1
    except EOFError:
        print("\nRelease stopped: input ended.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nRelease interrupted.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
