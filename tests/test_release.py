"""Exercise the maintainer release command against an isolated Git remote."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION = "v1.2.3"
TAG_REF = f"refs/tags/{VERSION}"


class ReleaseEntrypointTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "posix", "Direct script execution requires POSIX.")
    def test_release_script_runs_directly(self) -> None:
        result = subprocess.run(
            [str(REPO_ROOT / "release.py"), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("usage: release.py", result.stdout)


class ReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.repo = root / "repo"
        self.remote = root / "origin.git"
        self.repo.mkdir()
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.git("init", "--bare", str(self.remote))
        self.git("init", "--initial-branch=main")
        self.git("config", "user.name", "Release Test")
        self.git("config", "user.email", "release-test@example.invalid")
        shutil.copy2(REPO_ROOT / "release.py", self.repo)
        (self.repo / "scripts").mkdir()
        for name in ("__init__.py", "release_version.py"):
            shutil.copy2(REPO_ROOT / "scripts" / name, self.repo / "scripts")
        self.git("add", "release.py", "scripts")
        self.git("commit", "-m", "Release candidate")
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "origin", "main")

    def git(self, *args: str, cwd: Path | None = None) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd if cwd is not None else self.repo,
            env=self.env,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def release(self, answers: str = f"{VERSION}\nyes\n") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.repo / "release.py")],
            cwd=self.repo,
            env=dict(self.env, PYTHONDONTWRITEBYTECODE="1"),
            input=answers,
            capture_output=True,
            text=True,
        )

    def assert_no_release_tag(self) -> None:
        self.assertEqual("", self.git("tag", "--list", VERSION))
        self.assertEqual("", self.git("tag", "--list", VERSION, cwd=self.remote))

    def test_suggests_v1_for_an_untagged_origin(self) -> None:
        result = self.release("\nyes\n")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Latest stable tag on origin: none", result.stdout)
        self.assertIn("Release version [v1.0.0]", result.stdout)
        self.assertEqual("v1.0.0", self.git("tag", "--list", cwd=self.remote))

    def test_suggests_next_patch_from_highest_stable_origin_tag(self) -> None:
        remote_tags = ("v1.9.99", "v1.10.9", "v2.0.0-rc.1", "v20.0.0+build", "nightly")
        for tag in remote_tags:
            self.git("tag", tag)
        self.git("push", "origin", *(f"refs/tags/{tag}" for tag in remote_tags))
        self.git("tag", "-d", "v1.10.9")
        self.git("tag", "v99.0.0")

        result = self.release("\nyes\n")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Latest stable tag on origin: v1.10.9", result.stdout)
        self.assertIn("Release version [v1.10.10]", result.stdout)
        self.assertIn("v1.10.10", self.git("tag", "--list", cwd=self.remote).splitlines())

    def test_pushes_only_the_confirmed_annotated_tag(self) -> None:
        self.git("tag", "-a", "v0.0.1", "-m", "Do not publish")
        self.git("config", "push.followTags", "true")
        commit = self.git("rev-parse", "HEAD")
        result = self.release()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(f"{VERSION} -> {commit}", result.stdout)
        self.assertEqual(VERSION, self.git("tag", "--list", cwd=self.remote))
        self.assertEqual("tag", self.git("cat-file", "-t", TAG_REF, cwd=self.remote))
        self.assertEqual(commit, self.git("rev-parse", f"{TAG_REF}^{{commit}}", cwd=self.remote))

    def test_declining_leaves_both_repositories_untagged(self) -> None:
        result = self.release(f"{VERSION}\n\n")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Cancelled", result.stdout)
        self.assert_no_release_tag()

    def test_invalid_version_is_rejected(self) -> None:
        for version in ("1.2.3", "v1.2.3-rc..1"):
            with self.subTest(version=version):
                result = self.release(f"{version}\nyes\n")
                self.assertNotEqual(0, result.returncode)
                self.assertIn("Invalid version", result.stderr)
        self.assertEqual("", self.git("tag", "--list"))
        self.assertEqual("", self.git("tag", "--list", cwd=self.remote))

    def test_dirty_worktree_is_rejected(self) -> None:
        (self.repo / "notes.txt").write_text("untracked\n", encoding="utf-8")
        result = self.release()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("clean working tree", result.stderr)
        self.assert_no_release_tag()

    def test_non_main_branch_is_rejected(self) -> None:
        self.git("switch", "-c", "feature")
        result = self.release()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("main branch", result.stderr)
        self.assert_no_release_tag()

    def test_checks_current_remote_main_not_cached_tracking_ref(self) -> None:
        other = self.repo.parent / "other"
        self.git("clone", "--branch", "main", str(self.remote), str(other))
        self.git(
            "-c", "user.name=Release Test",
            "-c", "user.email=release-test@example.invalid",
            "commit", "--allow-empty", "-m", "Advance remote",
            cwd=other,
        )
        self.git("push", "origin", "main", cwd=other)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.git("rev-parse", "origin/main"))

        result = self.release()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("does not match origin/main", result.stderr)
        self.assert_no_release_tag()

    def test_existing_local_tag_is_rejected(self) -> None:
        self.git("tag", VERSION)
        result = self.release()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("already exists locally", result.stderr)
        self.assertEqual("", self.git("tag", "--list", cwd=self.remote))

    def test_existing_remote_tag_is_rejected(self) -> None:
        self.git("tag", VERSION)
        self.git("push", "origin", TAG_REF)
        self.git("tag", "-d", VERSION)

        result = self.release()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("already exists on origin", result.stderr)
        self.assertEqual("", self.git("tag", "--list"))

    def test_failed_push_reports_retained_local_tag(self) -> None:
        self.git("remote", "set-url", "--push", "origin", str(self.repo.parent / "missing"))
        result = self.release()
        self.assertNotEqual(0, result.returncode)
        self.assertIn(f"Local tag {VERSION} was kept", result.stderr)
        self.assertEqual(VERSION, self.git("tag", "--list"))
        self.assertEqual("", self.git("tag", "--list", cwd=self.remote))


if __name__ == "__main__":
    unittest.main()
