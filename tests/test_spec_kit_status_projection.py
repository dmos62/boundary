"""Focused tests for the Spec Kit read-only authorization status projection."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from boundary.authorization import (
    OperationRecord,
    OperationTargetEvidence,
    TaskWriteSet,
    capture_git_baseline,
    write_current_operation,
)
from boundary_host.adapter import status_feature


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
class SpecKitStatusProjectionTests(unittest.TestCase):
    def initialize(self, root: Path) -> None:
        run_git(root, "init", "-q")
        run_git(root, "config", "user.email", "tests@example.invalid")
        run_git(root, "config", "user.name", "Boundary Tests")
        (root / "app.py").write_text(
            "VALUE = 'before'\n",
            encoding="utf-8",
        )
        run_git(root, "add", "-A")
        run_git(root, "commit", "-q", "-m", "baseline")

    def feature(self, root: Path, change_id: str) -> Path:
        feature = root / "specs" / change_id
        feature.mkdir(parents=True)
        return feature

    def write_operation(self, root: Path, change_id: str) -> OperationRecord:
        record = OperationRecord(
            operation_id="operation-1",
            change_id=change_id,
            kind="implementation",
            tasks=(
                TaskWriteSet(
                    order=0,
                    task_id="T001",
                    story="US1",
                    writes=("app.py",),
                ),
            ),
            authorized_targets=(
                OperationTargetEvidence(
                    path="app.py",
                    owner="app",
                    effective_context_identity="sha256:context",
                ),
            ),
            contract_graph_identity="sha256:graph",
            git_baseline=capture_git_baseline(root),
            selected_task_ids=("T001",),
        )
        write_current_operation(root, record)
        return record

    def test_status_without_operation_has_no_feature_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            feature = self.feature(root, "001-active")

            status = status_feature(root, feature)

        self.assertIsNone(status.handoff)
        self.assertIsNone(status.change_matches_active_feature)

    def test_status_reports_matching_active_feature(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            feature = self.feature(root, "001-active")
            self.write_operation(root, "001-active")

            status = status_feature(root, feature)

        self.assertIsNotNone(status.handoff)
        assert status.handoff is not None
        self.assertEqual("001-active", status.handoff.change_id)
        self.assertTrue(status.change_matches_active_feature)

    def test_status_reports_operation_from_another_feature(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            feature = self.feature(root, "002-active")
            self.write_operation(root, "001-other")

            status = status_feature(root, feature)

        self.assertIsNotNone(status.handoff)
        self.assertFalse(status.change_matches_active_feature)


if __name__ == "__main__":
    unittest.main()
