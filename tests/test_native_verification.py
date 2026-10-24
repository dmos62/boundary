from boundary.cli.setup import update_managed_ignore
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from boundary.pre_change import (
    ChangeWriteSet,
    ContractEvolutionWriteSet,
    TaskWriteSet,
    open_contract_operation,
    open_implementation_operation,
    read_current_operation,
)
from boundary.post_change import (
    PostChangeError,
    close_verified_operation,
    check_operation_writes,
)


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


def write_source_contract(root: Path) -> None:
    path = root / "contracts" / "source.contract.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        "schema: boundary.contract/v1\n"
        "id: source\n"
        "owns:\n"
        "  - src/**\n"
        "applies_to: []\n"
        "depends_on: []\n"
        "---\n"
        "## Purpose\n\n"
        "Own source implementation.\n\n"
        "## Invariants\n\n"
        "- Source behavior remains explicit.\n",
        encoding="utf-8",
    )


def write_policy_contract(root: Path) -> None:
    path = root / "contracts" / "policy.contract.md"
    path.write_text(
        "---\n"
        "schema: boundary.contract/v1\n"
        "id: policy\n"
        "owns: []\n"
        "applies_to:\n"
        "  - src/**\n"
        "depends_on: []\n"
        "---\n"
        "## Invariants\n\n"
        "- New policy applies.\n",
        encoding="utf-8",
    )


def implementation_change(*paths: str) -> ChangeWriteSet:
    return ChangeWriteSet(
        "001-change",
        (
            TaskWriteSet(
                0,
                "T001",
                "US1",
                tuple(paths),
            ),
        ),
    )


def resolve_implementation_scope(root: Path, *paths: str):
    return open_implementation_operation(
        root,
        implementation_change(*paths),
        selected_task_ids=("T001",),
    )


@unittest.skipUnless(shutil.which("git"), "Git is required")
class NativeVerificationTests(unittest.TestCase):
    def initialize(self, root: Path) -> None:
        run_git(root, "init", "-q")
        update_managed_ignore(root, True)
        run_git(root, "config", "user.email", "tests@example.invalid")
        run_git(root, "config", "user.name", "Boundary Tests")
        write_source_contract(root)
        source = root / "src"
        source.mkdir()
        (source / "a.py").write_text("VALUE = 'a'\n", encoding="utf-8")
        (source / "b.py").write_text("VALUE = 'b'\n", encoding="utf-8")
        run_git(root, "add", "-A")
        run_git(root, "commit", "-q", "-m", "baseline")

    def test_authorized_actual_write_closes_operation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            resolve_implementation_scope(root, "src/a.py")
            (root / "src" / "a.py").write_text(
                "VALUE = 'changed'\n",
                encoding="utf-8",
            )

            result = check_operation_writes(root)
            verified = close_verified_operation(root)

        self.assertEqual(("src/a.py",), result.actual_paths)
        self.assertFalse(result.blocking)
        self.assertEqual("verified", verified.status)

    def test_rejects_undeclared_write_in_same_owner(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            resolve_implementation_scope(root, "src/a.py")
            (root / "src" / "b.py").write_text(
                "VALUE = 'undeclared'\n",
                encoding="utf-8",
            )

            with self.assertRaises(PostChangeError) as raised:
                close_verified_operation(root)
            current = read_current_operation(root)

        self.assertEqual("UNDECLARED_WRITE", raised.exception.code)
        self.assertEqual("open", current.status)

    def test_rejects_native_contract_change_during_implementation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            resolve_implementation_scope(root, "src/a.py")
            write_policy_contract(root)

            with self.assertRaises(PostChangeError) as raised:
                close_verified_operation(root)

        self.assertEqual("OPERATION_KIND_VIOLATION", raised.exception.code)

    def test_fresh_resolution_detects_changed_effective_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            resolve_implementation_scope(root, "src/a.py")
            (root / "src" / "a.py").write_text(
                "VALUE = 'changed'\n",
                encoding="utf-8",
            )
            write_policy_contract(root)

            result = check_operation_writes(root)

        codes = {item.code for item in result.diagnostics}
        self.assertIn("OPERATION_KIND_VIOLATION", codes)
        self.assertIn("CONTRACT_CONTEXT_CHANGED", codes)

    def test_unchanged_baseline_dirty_state_is_not_an_actual_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            note = root / "docs" / "note.md"
            note.parent.mkdir()
            note.write_text("preexisting\n", encoding="utf-8")
            resolve_implementation_scope(root, "src/a.py")

            result = check_operation_writes(root)

        self.assertEqual((), result.actual_paths)
        self.assertFalse(result.blocking)

    def test_generated_write_is_checked_as_ordinary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            resolve_implementation_scope(root, "src/a.py")
            generated = root / ".adapter" / "generated.json"
            generated.parent.mkdir()
            generated.write_text("{}\n", encoding="utf-8")
            result = check_operation_writes(root)
        self.assertTrue(result.blocking)
        self.assertIn("UNDECLARED_WRITE", {item.code for item in result.diagnostics})

    def test_contract_evolution_rejects_ordinary_project_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.initialize(root)
            open_contract_operation(
                root,
                ContractEvolutionWriteSet(
                    "001-change",
                    ("contracts/source.contract.md",),
                ),
            )
            (root / "src" / "a.py").write_text(
                "VALUE = 'wrong-kind'\n",
                encoding="utf-8",
            )

            with self.assertRaises(PostChangeError) as raised:
                close_verified_operation(root)

        self.assertEqual("OPERATION_KIND_VIOLATION", raised.exception.code)


if __name__ == "__main__":
    unittest.main()
