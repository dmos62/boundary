import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from boundary.authorization import (
    ChangeWriteSet,
    TaskWriteSet,
    authorize_implementation_operation,
    operation_archive_path,
)
from boundary.verification import finalize_operation_verification


def run_git(root: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


def write_contract(root: Path, contract_id: str, scope: str) -> None:
    path = root / "contracts" / f"{contract_id}.contract.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        "schema: boundary.contract/v1\n"
        f"id: {contract_id}\n"
        "owns:\n"
        f"  - {scope}\n"
        "applies_to: []\n"
        "depends_on: []\n"
        "---\n"
        "## Invariants\n\n"
        f"- {contract_id} behavior remains explicit.\n",
        encoding="utf-8",
    )


def change() -> ChangeWriteSet:
    return ChangeWriteSet(
        "003-change",
        (
            TaskWriteSet(
                0,
                "T009",
                "US1",
                ("src/alpha/a.py",),
            ),
            TaskWriteSet(
                1,
                "T012",
                "US1",
                ("src/beta/b.py",),
            ),
        ),
    )


@unittest.skipUnless(shutil.which("git"), "Git is required")
class TaskSelectedUnitLifecycleTests(unittest.TestCase):
    def initialize(self, root: Path) -> None:
        run_git(root, "init", "-q")
        run_git(root, "config", "user.email", "tests@example.invalid")
        run_git(root, "config", "user.name", "Boundary Tests")
        write_contract(root, "alpha", "src/alpha/**")
        write_contract(root, "beta", "src/beta/**")

        for relative, content in (
            ("src/alpha/a.py", "VALUE = 'a'\n"),
            ("src/beta/b.py", "VALUE = 'b'\n"),
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        run_git(root, "add", "-A")
        run_git(root, "commit", "-q", "-m", "baseline")

    def test_same_change_can_progress_through_sequential_units(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)

            first = authorize_implementation_operation(
                root,
                change(),
                selected_task_ids=("T009",),
            )
            (root / "src/alpha/a.py").write_text(
                "VALUE = 'first'\n",
                encoding="utf-8",
            )
            finalize_operation_verification(
                root,
                operation_id=first.operation_id,
            )

            second = authorize_implementation_operation(
                root,
                change(),
                selected_task_ids=("T012",),
            )
            self.assertEqual(("T012",), second.selected_task_ids)
            self.assertEqual(
                ("src/beta/b.py",),
                tuple(target.path for target in second.authorized_targets),
            )

            (root / "src/beta/b.py").write_text(
                "VALUE = 'second'\n",
                encoding="utf-8",
            )
            verified = finalize_operation_verification(
                root,
                operation_id=second.operation_id,
            )

        self.assertEqual("verified", verified.status)

    def test_scope_expansion_uses_fresh_selection_and_carry_forward(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)

            first = authorize_implementation_operation(
                root,
                change(),
                selected_task_ids=("T012",),
            )
            (root / "src/beta/b.py").write_text(
                "VALUE = 'selected'\n",
                encoding="utf-8",
            )
            finalize_operation_verification(root)
            archive = operation_archive_path(root, first.operation_id)

            successor = authorize_implementation_operation(
                root,
                change(),
                selected_task_ids=("T012", "T009"),
            )

            self.assertTrue(archive.is_file())
            self.assertEqual(
                ("T009", "T012"),
                successor.selected_task_ids,
            )
            self.assertEqual(
                ("src/alpha/a.py", "src/beta/b.py"),
                tuple(
                    target.path
                    for target in successor.authorized_targets
                ),
            )
            self.assertEqual(
                ("src/beta/b.py",),
                tuple(item.path for item in successor.carried_forward),
            )

    def test_selected_multi_owner_unit_records_each_owner(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)

            record = authorize_implementation_operation(
                root,
                change(),
                selected_task_ids=("T009", "T012"),
            )

        self.assertEqual(
            ("alpha", "beta"),
            tuple(
                target.owner
                for target in record.authorized_targets
            ),
        )


if __name__ == "__main__":
    unittest.main()
