"""Real Spec Kit 1.0.10 Linux downstream lifecycle coverage."""

from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

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


@unittest.skipUnless(platform.system() == "Linux", "Linux integration coverage")
class RealSpecKitLinuxLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for command in ("bash", "git", "uv", "specify"):
            if shutil.which(command) is None:
                raise unittest.SkipTest(f"{command} is required")
        version = run(["specify", "--version"], cwd=REPO_ROOT)
        pattern = rf"(^|[^0-9]){re.escape(SPECKIT_VERSION)}([^0-9]|$)"
        if version.returncode != 0 or re.search(
            pattern, version.stdout + version.stderr
        ) is None:
            raise unittest.SkipTest(
                f"Spec Kit {SPECKIT_VERSION} must already be installed"
            )

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.temp = Path(self.temporary.name)
        self.bin_dir = self.temp / "bin"
        self.bin_dir.mkdir()
        self._write_tool("codex")
        self.env = os.environ.copy()
        self.env["PATH"] = (
            str(self.bin_dir) + os.pathsep + self.env.get("PATH", "")
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_clean_install_uses_shell_and_passes_check(self):
        source = self._source_checkout()
        project = self._project("clean")
        self._adopt(project, source)

        installed = self._consumer(project, source, "install")
        self.assertEqual(0, installed.returncode, installed.stderr)
        checked = self._consumer(project, source, "check")
        self.assertEqual(0, checked.returncode, checked.stderr)

        self._assert_shell_mode(project)
        self._assert_gitignore(project)
        self._run_workflow_helper(project)

    def test_saved_ps_project_recovers_to_shell(self):
        if shutil.which("pwsh"):
            self.skipTest("requires a Linux host without pwsh")

        source = self._source_checkout()
        project = self._project("recovery")
        initialized = run(
            [
                "specify",
                "init",
                "--here",
                "--force",
                "--non-interactive",
                "--ignore-agent-tools",
                "--integration",
                "codex",
                "--script",
                "ps",
            ],
            cwd=project,
            env=self.env,
        )
        self.assertEqual(0, initialized.returncode, initialized.stderr)
        self._commit(project, "saved PowerShell Spec Kit project")
        self._adopt(project, source)

        self._write_tool("pwsh")
        installed = self._consumer(project, source, "install")
        self.assertEqual(0, installed.returncode, installed.stderr)
        (self.bin_dir / "pwsh").unlink()

        for command in ("install", "check"):
            failed = self._consumer(project, source, command)
            self.assertEqual(2, failed.returncode)
            self.assertIn(
                "Spec Kit PowerShell script mode requires pwsh",
                failed.stderr,
            )
            self.assertEqual("ps", self._script_mode(project))

        recovery_env = dict(self.env)
        recovery_env["BOUNDARY_SPECKIT_SCRIPT"] = "sh"
        recovered = self._consumer(
            project, source, "reinstall", env=recovery_env
        )
        self.assertEqual(0, recovered.returncode, recovered.stderr)
        checked = self._consumer(project, source, "check")
        self.assertEqual(0, checked.returncode, checked.stderr)

        self._assert_shell_mode(project)
        self.assertTrue((project / ".specify/scripts/powershell").is_dir())
        self._assert_gitignore(project)
        self._run_workflow_helper(project)

        status = self._status_paths(project)
        self.assertIn(".specify/init-options.json", status)
        self.assertTrue(
            any(path.startswith(".agents/skills/speckit-") for path in status)
        )
        self.assertFalse(
            any(path.startswith(".specify/boundary-runtime/") for path in status)
        )

    def _source_checkout(self):
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
        self._init_git(source)
        self._commit(source, "Boundary source fixture")
        return source

    def _project(self, name):
        project = self.temp / name
        project.mkdir()
        (project / "app.txt").write_text("fixture\n", encoding="utf-8")
        self._init_git(project)
        self._commit(project, "downstream fixture")
        return project

    def _init_git(self, root):
        for args in (
            ("init", "-q"),
            ("config", "user.email", "tests@example.invalid"),
            ("config", "user.name", "Boundary Tests"),
        ):
            result = run(["git", *args], cwd=root)
            self.assertEqual(0, result.returncode, result.stderr)

    def _commit(self, root, message):
        added = run(["git", "add", "-A"], cwd=root)
        self.assertEqual(0, added.returncode, added.stderr)
        committed = run(["git", "commit", "-q", "-m", message], cwd=root)
        self.assertEqual(0, committed.returncode, committed.stderr)

    def _adopt(self, project, source):
        adopted = self._consumer(project, source, "adopt")
        self.assertEqual(0, adopted.returncode, adopted.stderr)
        self._commit(project, "adopt Boundary")

    def _consumer(self, project, source, command, *, env=None):
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

    def _write_tool(self, name):
        path = self.bin_dir / name
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        path.chmod(0o755)

    def _script_mode(self, project):
        options = json.loads(
            (project / ".specify/init-options.json").read_text(
                encoding="utf-8"
            )
        )
        return options["script"]

    def _assert_shell_mode(self, project):
        self.assertEqual("sh", self._script_mode(project))
        self.assertTrue((project / ".specify/scripts/bash").is_dir())
        plan = (
            project / ".agents/skills/speckit-plan/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn(".specify/scripts/bash/", plan)
        self.assertNotIn(".specify/scripts/powershell/", plan)

    def _assert_gitignore(self, project):
        content = (project / ".specify/.gitignore").read_text(
            encoding="utf-8"
        )
        self.assertIn("\nfeature.json\n", "\n" + content)
        self.assertIn("extensions/*/local-config.yml", content)

    def _run_workflow_helper(self, project):
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
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("SPEC_FILE", json.loads(result.stdout))

    def _status_paths(self, project):
        status = run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=project,
        )
        self.assertEqual(0, status.returncode, status.stderr)
        return {
            line[3:]
            for line in status.stdout.splitlines()
            if len(line) >= 4
        }


if __name__ == "__main__":
    unittest.main()
