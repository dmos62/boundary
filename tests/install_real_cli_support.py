"""Shared fixture helpers for real Spec Kit downstream lifecycle tests."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
SPECKIT_VERSION = "1.0.10"


def run(command, *, cwd, env=None):
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


class RealSpecKitFixtureMixin:
    def set_up_real_cli_fixture(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.temp = Path(self.temporary.name)
        self.bin_dir = self.temp / "bin"
        self.bin_dir.mkdir()
        self.write_tool("codex")
        self.env = os.environ.copy()
        self.env["PATH"] = (
            str(self.bin_dir) + os.pathsep + self.env.get("PATH", "")
        )

    def tear_down_real_cli_fixture(self):
        self.temporary.cleanup()

    def assert_success(self, result):
        self.assertEqual(
            0,
            result.returncode,
            result.stdout + result.stderr,
        )

    def source_checkout(self):
        source = self.temp / "boundary"
        shutil.copytree(
            REPO_ROOT,
            source,
            ignore=shutil.ignore_patterns(
                ".git",
                ".agents",
                ".specify",
                ".specdd",
                ".venv",
                "__pycache__",
                "*.pyc",
            ),
        )
        self.init_git(source)
        self.commit(source, "Boundary source fixture")
        return source

    def project(self, name):
        project = self.temp / name
        project.mkdir()
        (project / "app.txt").write_text("fixture\n", encoding="utf-8")
        self.init_git(project)
        self.commit(project, "downstream fixture")
        return project

    def init_git(self, root):
        for args in (
            ("init", "-q"),
            ("config", "user.email", "tests@example.invalid"),
            ("config", "user.name", "Boundary Tests"),
        ):
            result = run(["git", *args], cwd=root)
            self.assert_success(result)

    def commit(self, root, message):
        added = run(["git", "add", "-A"], cwd=root)
        self.assert_success(added)
        committed = run(["git", "commit", "-q", "-m", message], cwd=root)
        self.assert_success(committed)

    def adopt(self, project, source):
        adopted = self.consumer(project, source, "adopt")
        self.assert_success(adopted)
        self.commit(project, "adopt Boundary")

    def consumer(self, project, source, command, *, env=None):
        return run(
            [
                sys.executable,
                str(source / "scripts/consumer.py"),
                "--root",
                str(project),
                command,
            ],
            cwd=source,
            env=env or self.env,
        )

    def write_tool(self, name):
        path = self.bin_dir / name
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        path.chmod(0o755)

    def script_mode(self, project):
        options = json.loads(
            (project / ".specify/init-options.json").read_text(
                encoding="utf-8"
            )
        )
        return options["script"]

    def assert_shell_mode(self, project):
        self.assertEqual("sh", self.script_mode(project))
        self.assertTrue((project / ".specify/scripts/bash").is_dir())
        plan = (
            project / ".agents/skills/speckit-plan/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn(".specify/scripts/bash/", plan)
        self.assertNotIn(".specify/scripts/powershell/", plan)

    def assert_gitignore(self, project):
        content = (project / ".specify/.gitignore").read_text(
            encoding="utf-8"
        )
        self.assertIn("\nfeature.json\n", "\n" + content)
        self.assertIn("extensions/*/local-config.yml", content)

    def assert_tracked(self, project, relative_path):
        result = run(
            [
                "git",
                "ls-files",
                "--error-unmatch",
                "--",
                relative_path,
            ],
            cwd=project,
        )
        self.assert_success(result)

    def assert_not_ignored(self, project, relative_path):
        result = run(
            [
                "git",
                "check-ignore",
                "--no-index",
                "-q",
                "--",
                relative_path,
            ],
            cwd=project,
        )
        self.assertEqual(
            1,
            result.returncode,
            result.stdout + result.stderr,
        )

    def tree_snapshot(self, root):
        return {
            path.relative_to(root).as_posix(): (
                path.stat().st_mode & 0o7777,
                path.read_bytes(),
            )
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    def run_workflow_helper(self, project):
        result = run(
            [
                "bash",
                ".specify/scripts/bash/create-new-feature.sh",
                "--json",
                "--dry-run",
                "--short-name",
                "recovery-smoke",
                "Recovery smoke",
            ],
            cwd=project,
            env=self.env,
        )
        self.assert_success(result)
        self.assertIn("SPEC_FILE", json.loads(result.stdout))

    def status_lines(self, project):
        status = run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=project,
        )
        self.assert_success(status)
        return status.stdout.splitlines()
