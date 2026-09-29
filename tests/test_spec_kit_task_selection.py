import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
SCRIPT_ROOT = REPOSITORY_ROOT / "integration" / "speckit" / "scripts"
for path in (SCRIPT_ROOT, SOURCE_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from boundary.verification import VerificationError
from spec_kit_adapter import (
    SpecKitAdapterError,
    authorize_feature,
    verify_feature,
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


def initialize(root: Path) -> Path:
    run_git(root, "init", "-q")
    run_git(root, "config", "user.email", "tests@example.invalid")
    run_git(root, "config", "user.name", "Boundary Tests")

    contract = root / "contracts" / "app.contract.md"
    contract.parent.mkdir(parents=True)
    contract.write_text(
        "---\n"
        "schema: boundary.contract/v1\n"
        "id: app\n"
        "owns:\n"
        "  - src/**\n"
        "applies_to: []\n"
        "depends_on: []\n"
        "---\n"
        "## Invariants\n\n"
        "- Application behavior remains explicit.\n",
        encoding="utf-8",
    )

    source = root / "src"
    source.mkdir()
    (source / "a.py").write_text("VALUE = 'a'\n", encoding="utf-8")
    (source / "b.py").write_text("VALUE = 'b'\n", encoding="utf-8")

    feature = root / "specs" / "003-change"
    feature.mkdir(parents=True)
    (feature / "tasks.md").write_text(
        "# Tasks\n\n"
        "- [ ] T009 [US1] Existing implementation\n"
        "  Writes: `src/a.py`\n"
        "- [ ] T012 [US1] Current implementation\n"
        "  Writes: `src/b.py`\n",
        encoding="utf-8",
    )

    run_git(root, "add", "-A")
    run_git(root, "commit", "-q", "-m", "baseline")
    return feature


@unittest.skipUnless(shutil.which("git"), "Git is required")
class SpecKitTaskSelectionTests(unittest.TestCase):
    def test_missing_unknown_and_duplicate_selection_are_blocking(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            feature = initialize(root)

            with self.assertRaisesRegex(
                SpecKitAdapterError,
                "at least one selected task",
            ):
                authorize_feature(root, feature, ())
            with self.assertRaisesRegex(
                SpecKitAdapterError,
                "not present",
            ):
                authorize_feature(root, feature, ("T999",))
            with self.assertRaisesRegex(
                SpecKitAdapterError,
                "duplicates",
            ):
                authorize_feature(root, feature, ("T012", "T012"))

    def test_unselected_task_does_not_contribute_authority(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            feature = initialize(root)

            record = authorize_feature(root, feature, ("T012",))

        self.assertEqual(("T012",), record.selected_task_ids)
        self.assertEqual(
            ("src/b.py",),
            tuple(target.path for target in record.authorized_targets),
        )

    def test_changed_task_projection_does_not_widen_active_operation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            feature = initialize(root)
            authorize_feature(root, feature, ("T012",))

            (feature / "tasks.md").write_text(
                "# Tasks\n\n"
                "- [ ] T009 [US1] Existing implementation\n"
                "  Writes: `src/a.py`\n"
                "- [ ] T012 [US1] Current implementation\n"
                "  Writes: `src/b.py`, `src/a.py`\n",
                encoding="utf-8",
            )
            (root / "src/a.py").write_text(
                "VALUE = 'not-authorized'\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                VerificationError,
                "UNDECLARED_WRITE",
            ):
                verify_feature(root, feature)


if __name__ == "__main__":
    unittest.main()
