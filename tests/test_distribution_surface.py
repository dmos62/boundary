"""Tests for the installed Boundary product command surface."""

from __future__ import annotations

import shutil
import subprocess
import unittest

from boundary.cli import build_parser


class DistributionSurfaceTests(unittest.TestCase):
    def test_cli_exposes_semantic_distribution_and_lifecycle_commands(self) -> None:
        parser = build_parser()

        authorize = parser.parse_args(["authorize", "T001", "T002"])
        self.assertEqual("authorize", authorize.command)
        self.assertEqual(["T001", "T002"], authorize.task_ids)

        inspect = parser.parse_args(["inspect", "--authorized"])
        self.assertEqual("inspect", inspect.command)
        self.assertTrue(inspect.authorized)
        self.assertEqual([], inspect.targets)

        verify = parser.parse_args(["verify"])
        self.assertEqual("verify", verify.command)

        status = parser.parse_args(["status"])
        self.assertEqual("status", status.command)

        contracts = parser.parse_args(["contracts", "check"])
        self.assertEqual("check", contracts.contracts_command)

        integration = parser.parse_args(["integration", "check"])
        self.assertEqual("check", integration.integration_command)

    def test_top_level_help_exposes_boundary_lifecycle(self) -> None:
        help_text = build_parser().format_help()

        self.assertIn("Routine implementation lifecycle:", help_text)
        self.assertIn("boundary authorize T012 [T013 ...]", help_text)
        self.assertIn("boundary inspect --authorized", help_text)
        self.assertIn("boundary verify", help_text)
        self.assertIn("Situational queries:", help_text)
        self.assertIn("boundary status", help_text)
        self.assertIn("Maintenance:", help_text)

    @unittest.skipUnless(shutil.which("boundary"), "installed boundary command required")
    def test_installed_authorize_help_requires_explicit_task_selection(self) -> None:
        result = subprocess.run(
            ["boundary", "authorize", "--help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("usage: boundary authorize [-h] [TASK_ID ...]", result.stdout)
        self.assertIn("pass one or more task IDs", result.stdout)
        self.assertIn("positionally", result.stdout)
        self.assertNotIn("--task TASK_ID", result.stdout)

    def test_status_help_keeps_status_out_of_routine_entry(self) -> None:
        parser = build_parser()
        status_parser = next(
            action.choices["status"]
            for action in parser._actions
            if getattr(action, "choices", None)
            and "status" in action.choices
        )
        help_text = status_parser.format_help()

        self.assertIn("recovery, handoff", help_text)
        self.assertIn("rather than the routine implementation path", help_text)


if __name__ == "__main__":
    unittest.main()
