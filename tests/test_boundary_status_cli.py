import io
import json
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

from boundary.authorization import (
    OperationRecord,
    OperationTargetEvidence,
    TaskWriteSet,
    capture_git_baseline,
    write_current_operation,
)
from boundary.cli import main


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
class BoundaryStatusCliTests(unittest.TestCase):
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

    def run_status(self, root: Path) -> tuple[int, str, str]:
        output = io.StringIO()
        errors = io.StringIO()
        code = main(
            ["status"],
            repository_root=root,
            stdout=output,
            stderr=errors,
        )
        return code, output.getvalue(), errors.getvalue()

    def test_status_returns_json_null_without_current_operation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)

            code, output, errors = self.run_status(root)

        self.assertEqual(0, code)
        self.assertEqual("null\n", output)
        self.assertEqual("", errors)

    def test_status_emits_compact_authorization_handoff(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            record = self.write_operation(root)

            code, output, errors = self.run_status(root)
            document = json.loads(output)

        self.assertEqual(0, code)
        self.assertEqual("", errors)
        self.assertEqual(
            "boundary.authorization-handoff/v1",
            document["schema"],
        )
        self.assertEqual(record.operation_id, document["operationId"])
        self.assertEqual(["T001"], document["selectedTaskIds"])
        self.assertEqual(
            ["app.py"],
            [item["path"] for item in document["authorizedTargets"]],
        )
        self.assertTrue(document["git"]["headMatchesBaseline"])

    def test_status_reports_when_head_changed_since_authorization(self):
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

            code, output, errors = self.run_status(root)
            document = json.loads(output)

        self.assertEqual(0, code)
        self.assertEqual("", errors)
        self.assertFalse(document["git"]["headMatchesBaseline"])
        self.assertNotEqual(
            document["git"]["baselineHead"],
            document["git"]["currentHead"],
        )


if __name__ == "__main__":
    unittest.main()
