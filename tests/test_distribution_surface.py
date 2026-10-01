"""Focused source-level checks for the mise-native distribution surface."""

from __future__ import annotations

from pathlib import Path
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

    def test_mise_uses_git_backed_pipx_for_pinned_speckit(self) -> None:
        config = tomllib.loads(
            (ROOT / "mise.toml").read_text(encoding="utf-8")
        )
        tools = config["tools"]
        key = "pipx:git+https://github.com/github/spec-kit.git"
        self.assertEqual("v1.0.10", tools[key]["version"])

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

    def test_workflow_uses_installed_boundary_command_directly(self) -> None:
        source = (
            ROOT / "integration" / "speckit" / "workflow-overlay.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("boundary authorize", source)
        self.assertIn("boundary verify", source)
        self.assertNotIn(".boundary/bin/boundary", source)
        self.assertNotIn("uv run --no-project", source)
        self.assertNotIn("adapter_gate.py", source)

    def test_generated_excludes_drop_retired_runtime_and_launcher(self) -> None:
        self.assertNotIn("/.boundary/", GENERATED_EXCLUDES)
        self.assertNotIn("/.specify/boundary-runtime/", GENERATED_EXCLUDES)

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
        ):
            self.assertFalse((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
