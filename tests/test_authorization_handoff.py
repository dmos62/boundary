from boundary.cli.setup import update_managed_ignore
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from boundary.pre_change import (
    OperationRecord,
    OperationTargetEvidence,
    TaskWriteSet,
    capture_git_baseline,
    read_operation_status,
    write_current_operation,
)


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
class OperationStatusTests(unittest.TestCase):
    def initialize(self, root: Path) -> None:
        run_git(root, "init", "-q")
        update_managed_ignore(root, True)
        run_git(root, "config", "user.email", "tests@example.invalid")
        run_git(root, "config", "user.name", "Boundary Tests")
        (root / "app.py").write_text(
            "VALUE = 'before'\n",
            encoding="utf-8",
        )
        run_git(root, "add", "-A")
        run_git(root, "commit", "-q", "-m", "baseline")

    def write_operation(self, root: Path) -> OperationRecord:
        record = OperationRecord(
            operation_id="operation-1",
            change_id="001-change",
            kind="implementation",
            tasks=(
                TaskWriteSet(
                    order=0,
                    task_id="T001",
                    story="US1",
                    writes=("app.py",),
                ),
            ),
            allowed_targets=(
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

    def test_returns_none_without_current_operation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)

            self.assertIsNone(read_operation_status(root))

    def test_projects_compact_current_authorization_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            record = self.write_operation(root)

            handoff = read_operation_status(root)

        self.assertIsNotNone(handoff)
        assert handoff is not None
        self.assertEqual(record.operation_id, handoff.operation_id)
        self.assertEqual(("T001",), handoff.selected_task_ids)
        self.assertEqual(
            ("app.py",),
            tuple(target.path for target in handoff.allowed_targets),
        )
        self.assertTrue(handoff.head_matches_baseline)
        document = handoff.to_document()
        self.assertEqual(
            "boundary.operation-status/v2",
            document["schema"],
        )

    def test_reports_when_head_no_longer_matches_baseline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            self.write_operation(root)

            (root / "app.py").write_text(
                "VALUE = 'after'\n",
                encoding="utf-8",
            )
            run_git(root, "add", "app.py")
            run_git(root, "commit", "-q", "-m", "advance head")

            handoff = read_operation_status(root)

        self.assertIsNotNone(handoff)
        assert handoff is not None
        self.assertFalse(handoff.head_matches_baseline)
        self.assertNotEqual(handoff.baseline_head, handoff.current_head)


if __name__ == "__main__":
    unittest.main()
