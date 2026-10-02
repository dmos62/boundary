"""Focused source-level checks for the mise-native distribution surface."""

from __future__ import annotations

from importlib.metadata import version as distribution_version
from pathlib import Path
import shutil
import subprocess
import tomllib
import unittest

from boundary.cli import build_parser
from boundary_host.generated_state import GENERATED_EXCLUDES

ROOT = Path(__file__).resolve().parents[1]


class DistributionSurfaceTests(unittest.TestCase):
    def test_package_exposes_boundary_console_script(self) -> None:
        config = tomllib.loads(
            (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        self.assertEqual("boundary-cli", config["project"]["name"])
        self.assertEqual(
            "boundary.cli:main",
            config["project"]["scripts"]["boundary"],
        )
        self.assertEqual(
            [
                "src/boundary",
                "integration/speckit/runtime/boundary_host",
            ],
            config["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"],
        )

    def test_source_repository_uses_editable_development_install(self) -> None:
        config = tomllib.loads(
            (ROOT / "mise.toml").read_text(encoding="utf-8")
        )
        tools = config["tools"]
        speckit = "pipx:git+https\://github.com/github/spec-kit.git"
        self.assertEqual("v1.0.10", tools[speckit]["version"])
        self.assertFalse(
            any(
                key.startswith(
                    "pipx:git+https\://github.com/specdd/speckit-boundary"
                )
                for key in tools
            )
        )
        self.assertEqual(
            "uv pip install --editable .",
            config["tasks"]["dev-install"]["run"],
        )

    def test_downstream_setup_uses_portable_git_source_and_mise_lock(self) -> None:
        source = (ROOT / "docs" / "setup-downstream.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "pipx:git+https\://github.com/specdd/speckit-boundary.git",
            source,
        )
        self.assertIn("mise install --locked", source)
        self.assertIn("mise lock --bump", source)
        self.assertNotIn("boundary.lock.json", source)
        self.assertNotIn("file://", source)
        self.assertNotIn(".boundary/bin/boundary", source)

    def test_cli_exposes_semantic_distribution_and_lifecycle_commands(self) -> None:
        parser = build_parser()

        authorize = parser.parse_args(
            ["authorize", "--task", "T001", "--task", "T002"]
        )
        self.assertEqual(["T001", "T002"], authorize.task_ids)

        integration = parser.parse_args(["integration", "install"])
        self.assertEqual("install", integration.integration_command)

        verify = parser.parse_args(["verify"])
        self.assertEqual("verify", verify.command)

    def test_top_level_help_exposes_boundary_lifecycle(self) -> None:
        help_text = " ".join(build_parser().format_help().split())

        self.assertIn(
            "Persistent project contracts and operation authorization for coding agents.",
            help_text,
        )
        self.assertIn("--version", help_text)
        self.assertIn(
            "Show the installed Boundary distribution version and exit.",
            help_text,
        )
        self.assertIn("Implementation lifecycle:", help_text)
        for command in (
            "boundary inspect <target...>",
            "boundary authorize --task <task-id> [--task <task-id> ...]",
            "boundary verify",
            "boundary status",
            "boundary contracts check",
            "boundary integration install|check|remove",
        ):
            self.assertIn(command, help_text)

    @unittest.skipUnless(shutil.which("boundary"), "boundary CLI is not installed")
    def test_installed_version_reports_distribution_metadata(self) -> None:
        result = subprocess.run(
            ["boundary", "--version"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            f"boundary {distribution_version('boundary-cli')}\n",
            result.stdout,
        )
        self.assertEqual("", result.stderr)

    @unittest.skipUnless(shutil.which("boundary"), "boundary CLI is not installed")
    def test_installed_authorize_help_requires_explicit_task_selection(self) -> None:
        result = subprocess.run(
            ["boundary", "authorize", "--help"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("--task TASK_ID", result.stdout)
        self.assertIn("Pass --task at least once", result.stdout)
        self.assertIn("Explicit task selection is required", result.stdout)

    def test_workflow_uses_installed_boundary_command_directly(self) -> None:
        source = (
            ROOT / "integration" / "speckit" / "workflow-overlay.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("boundary authorize", source)
        self.assertIn("boundary verify", source)
        self.assertNotIn(".boundary/bin/boundary", source)
        self.assertNotIn("uv run --no-project", source)
        self.assertNotIn("adapter_gate.py", source)

    def test_generated_excludes_cover_only_current_generated_state(self) -> None:
        self.assertNotIn("/.boundary/", GENERATED_EXCLUDES)
        self.assertNotIn("/.specify/boundary-runtime/", GENERATED_EXCLUDES)
        self.assertIn("/.agents/skills/boundary-scope/", GENERATED_EXCLUDES)
        self.assertIn("/.specify/extensions/boundary/", GENERATED_EXCLUDES)

    def test_legacy_distribution_scripts_are_removed(self) -> None:
        for relative in (
            "scripts/consumer.py",
            "scripts/consumer_lock.py",
            "scripts/consumer_source.py",
            "scripts/consumer_state.py",
            "scripts/project_boundary.py",
            "scripts/install-source.sh",
            "scripts/install-host.sh",
            "scripts/install.sh",
            "scripts/bootstrap.sh",
        ):
            self.assertFalse((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
