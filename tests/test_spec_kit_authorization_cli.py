"""Focused regression tests for Spec Kit implementation-unit authorization."""

from __future__ import annotations

import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from boundary.cli import main
from boundary_host.commands import run_authorize


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout.strip()


@unittest.skipUnless(shutil.which("git"), "Git is required")
class SpecKitAuthorizationCliTests(unittest.TestCase):
    def initialize(self, root: Path) -> None:
        run_git(root, "init", "-q")
        feature = root / "specs" / "001-example"
        feature.mkdir(parents=True)
        (feature / "tasks.md").write_text(
            "- [ ] T001 [US1] Update app\n"
            "  Writes: `src/app.py`\n"
            "- [ ] T002 [US1] Update config\n"
            "  Writes: `src/config.py`\n",
            encoding="utf-8",
        )
        contracts = root / "contracts"
        contracts.mkdir()
        (contracts / "app.contract.md").write_text(
            "---\n"
            "schema: boundary.contract/v1\n"
            "id: app\n"
            "owns:\n"
            "  - src/**\n"
            "---\n\n"
            "## Invariants\n\n"
            "- Application source remains owned.\n",
            encoding="utf-8",
        )

    def run_cli(
        self,
        root: Path,
        *arguments: str,
        boundary_task_ids: str | None = None,
    ) -> tuple[int, str, str]:
        output = io.StringIO()
        errors = io.StringIO()
        environment = {"SPECIFY_FEATURE_DIRECTORY": "specs/001-example"}
        if boundary_task_ids is not None:
            environment["BOUNDARY_TASK_IDS"] = boundary_task_ids
        with patch.dict(os.environ, environment, clear=False):
            if boundary_task_ids is None:
                os.environ.pop("BOUNDARY_TASK_IDS", None)
            code = main(
                arguments,
                repository_root=root,
                stdout=output,
                stderr=errors,
            )
        return code, output.getvalue(), errors.getvalue()

    def run_adapter(
        self,
        root: Path,
        task_ids: str | tuple[str, ...],
    ) -> tuple[int, str, str]:
        output = io.StringIO()
        errors = io.StringIO()
        with patch.dict(
            os.environ,
            {"SPECIFY_FEATURE_DIRECTORY": "specs/001-example"},
            clear=False,
        ):
            os.environ.pop("BOUNDARY_TASK_IDS", None)
            code = run_authorize(root, task_ids, output, errors)
        return code, output.getvalue(), errors.getvalue()

    def assert_authorized(
        self,
        document: dict[str, object],
        tasks: list[str],
        targets: list[str],
    ) -> None:
        self.assertEqual("boundary.lifecycle-result/v1", document["schema"])
        self.assertEqual("authorized", document["status"])
        self.assertEqual("authorize", document["stage"])
        self.assertEqual(tasks, document["selectedTaskIds"])
        self.assertEqual(targets, document["authorizedTargets"])
        self.assertEqual([], document["diagnostics"])
        self.assertNotIn("operation", document)

    def test_cli_authorize_accepts_one_positional_selected_task(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.initialize(root)
            code, output, errors = self.run_cli(
                root,
                "authorize",
                "T001",
            )
            document = json.loads(output)

        self.assertEqual(0, code, errors)
        self.assert_authorized(document, ["T001"], ["src/app.py"])

    def test_adapter_normalizes_scalar_single_task_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.initialize(root)
            code, output, errors = self.run_adapter(root, "T001")
            document = json.loads(output)

        self.assertEqual(0, code, errors)
        self.assert_authorized(document, ["T001"], ["src/app.py"])

    def test_multiple_positional_tasks_use_canonical_host_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.initialize(root)
            code, output, errors = self.run_cli(
                root,
                "authorize",
                "T002",
                "T001",
            )
            document = json.loads(output)

        self.assertEqual(0, code, errors)
        self.assert_authorized(
            document,
            ["T001", "T002"],
            ["src/app.py", "src/config.py"],
        )

    def test_positional_selection_takes_precedence_over_workflow_transport(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.initialize(root)
            code, output, errors = self.run_cli(
                root,
                "authorize",
                "T001",
                boundary_task_ids='["T002"]',
            )
            document = json.loads(output)

        self.assertEqual(0, code, errors)
        self.assert_authorized(document, ["T001"], ["src/app.py"])

    def test_workflow_transport_is_used_only_without_positional_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.initialize(root)
            code, output, errors = self.run_cli(
                root,
                "authorize",
                boundary_task_ids='["T002"]',
            )
            document = json.loads(output)

        self.assertEqual(0, code, errors)
        self.assert_authorized(document, ["T002"], ["src/config.py"])

    def test_missing_task_selection_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.initialize(root)
            code, output, _ = self.run_cli(root, "authorize")
            document = json.loads(output)

        self.assertEqual(2, code)
        self.assertEqual("boundary.lifecycle-result/v1", document["schema"])
        self.assertEqual("blocked", document["status"])
        self.assertEqual("authorize", document["stage"])
        self.assertEqual("INVALID_TASK_SELECTION", document["code"])

    def test_unknown_positional_task_selection_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.initialize(root)
            code, output, _ = self.run_cli(root, "authorize", "T999")
            document = json.loads(output)

        self.assertEqual(2, code)
        self.assertEqual("blocked", document["status"])
        self.assertEqual("authorize", document["stage"])
        self.assertEqual("INVALID_TASK_SELECTION", document["code"])


if __name__ == "__main__":
    unittest.main()
