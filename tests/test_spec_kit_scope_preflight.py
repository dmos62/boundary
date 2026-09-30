import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
SCRIPT_ROOT = REPOSITORY_ROOT / "integration" / "speckit" / "scripts"
for path in (SCRIPT_ROOT, SOURCE_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from adapter_gate import run_stage
from boundary.authorization import read_current_operation
from boundary.verification import VerificationError
from spec_kit_adapter import (
    SpecKitAdapterError,
    authorize_feature,
    preflight_declared_scope,
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


def write_contract(
    root: Path,
    contract_id: str,
    scopes: tuple[str, ...],
) -> None:
    path = root / "contracts" / f"{contract_id}.contract.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    owns = "".join(f"  - {scope}\n" for scope in scopes)
    path.write_text(
        "---\n"
        "schema: boundary.contract/v1\n"
        f"id: {contract_id}\n"
        "owns:\n"
        f"{owns}"
        "applies_to: []\n"
        "depends_on: []\n"
        "---\n"
        "## Invariants\n\n"
        "- Declared writes remain explicit.\n",
        encoding="utf-8",
    )


def initialize(root: Path, *, own_records: bool = False) -> Path:
    run_git(root, "init", "-q")
    run_git(root, "config", "user.email", "tests@example.invalid")
    run_git(root, "config", "user.name", "Boundary Tests")

    write_contract(root, "app", ("src/**",))
    if own_records:
        write_contract(
            root,
            "project-records",
            ("specs/CONTINUATION.md", "BOUNDARY-FEEDBACK.md"),
        )

    source = root / "src"
    source.mkdir()
    (source / "a.py").write_text(
        "VALUE = 'before'\n",
        encoding="utf-8",
    )

    feature = root / "specs" / "004-preflight"
    feature.mkdir(parents=True)
    (feature / "tasks.md").write_text(
        "# Tasks\n\n"
        "- [ ] T001 [US1] Change application\n"
        "  Writes: `src/a.py`\n"
        "- [ ] T002 [US1] Update durable workflow records\n"
        "  Writes: `specs/CONTINUATION.md`, `BOUNDARY-FEEDBACK.md`\n",
        encoding="utf-8",
    )

    run_git(root, "add", "-A")
    run_git(root, "commit", "-q", "-m", "baseline")
    return feature


@unittest.skipUnless(shutil.which("git"), "Git is required")
class SpecKitDeclaredScopePreflightTests(unittest.TestCase):
    def test_preflight_surfaces_unowned_durable_records_without_operation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            feature = initialize(root)

            with self.assertRaisesRegex(
                SpecKitAdapterError,
                (
                    "unowned declared targets: "
                    "specs/CONTINUATION.md, BOUNDARY-FEEDBACK.md"
                ),
            ):
                preflight_declared_scope(root, feature)

            self.assertIsNone(read_current_operation(root))

    def test_preflight_surfaces_ambiguous_contract_graph_without_operation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            feature = initialize(root)
            write_contract(root, "records-a", ("BOUNDARY-FEEDBACK.md",))
            write_contract(root, "records-b", ("BOUNDARY-FEEDBACK.md",))

            with self.assertRaisesRegex(
                SpecKitAdapterError,
                "ambiguous ownership",
            ):
                preflight_declared_scope(root, feature)

            self.assertIsNone(read_current_operation(root))

    def test_preflight_inspection_grants_no_authority_to_unselected_task(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            feature = initialize(root, own_records=True)
            relative_feature = feature.relative_to(root).as_posix()

            with mock.patch.dict(
                os.environ,
                {"SPECIFY_FEATURE_DIRECTORY": relative_feature},
            ):
                result = run_stage(root, "preflight")

            targets = result["preflight"]["targets"]
            self.assertEqual(
                [
                    "src/a.py",
                    "specs/CONTINUATION.md",
                    "BOUNDARY-FEEDBACK.md",
                ],
                [target["path"] for target in targets],
            )
            self.assertIsNone(read_current_operation(root))

            authorized = authorize_feature(root, feature, ("T001",))
            self.assertEqual(("T001",), authorized.selected_task_ids)
            self.assertEqual(
                ("src/a.py",),
                tuple(
                    target.path
                    for target in authorized.authorized_targets
                ),
            )

            (root / "BOUNDARY-FEEDBACK.md").write_text(
                "not authorized by preflight\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                VerificationError,
                "UNDECLARED_WRITE",
            ):
                verify_feature(root, feature)


if __name__ == "__main__":
    unittest.main()
