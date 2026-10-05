"""Regression coverage for historical Boundary operation-record compatibility."""

from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from boundary.authorization import (
    AuthorizationError,
    ChangeWriteSet,
    TaskWriteSet,
    authorize_implementation_operation,
)
from boundary.authorization.codec import operation_record_from_document
from boundary.cli.main import main


_MISSING = object()


class OperationRecordCompatibilityTests(unittest.TestCase):
    def test_missing_selection_is_derived_from_historical_task_evidence(self) -> None:
        record = operation_record_from_document(
            _operation_document(("T001", "T002"))
        )

        self.assertEqual(("T001", "T002"), record.selected_task_ids)
        self.assertEqual(
            ["T001", "T002"],
            record.to_document()["selectedTaskIds"],
        )

    def test_status_accepts_legacy_single_task_scalar_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _init_git(root)
            _write_current(
                root,
                _operation_document(
                    ("T022",),
                    selected_task_ids="T022",
                ),
            )

            output = StringIO()
            errors = StringIO()
            result = main(
                ["status"],
                repository_root=root,
                stdout=output,
                stderr=errors,
            )

            self.assertEqual(0, result, errors.getvalue())
            document = json.loads(output.getvalue())
            self.assertEqual(["T022"], document["selectedTaskIds"])

    def test_authorization_can_replace_verified_legacy_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _init_git(root)
            _write_contract(root)
            _write_current(
                root,
                _operation_document(
                    ("T001", "T002"),
                    status="verified",
                ),
            )

            change = ChangeWriteSet(
                change_id="001-desktop-text-execution",
                tasks=(
                    TaskWriteSet(
                        order=0,
                        task_id="T022",
                        story=None,
                        writes=("src/t022.py",),
                    ),
                ),
            )

            record = authorize_implementation_operation(
                root,
                change,
                selected_task_ids=("T022",),
                operation_id="replacement",
            )

            self.assertEqual(("T022",), record.selected_task_ids)
            self.assertEqual(
                ("src/t022.py",),
                tuple(target.path for target in record.authorized_targets),
            )
            self.assertEqual(
                ["T022"],
                record.to_document()["selectedTaskIds"],
            )

    def test_scalar_selection_cannot_hide_mismatched_task_evidence(self) -> None:
        with self.assertRaisesRegex(
            AuthorizationError,
            "selected task identities must match operation task evidence",
        ):
            operation_record_from_document(
                _operation_document(
                    ("T001", "T002"),
                    selected_task_ids="T001",
                )
            )

    def test_null_selection_is_not_treated_as_missing(self) -> None:
        with self.assertRaisesRegex(
            AuthorizationError,
            "selectedTaskIds must be an array",
        ):
            operation_record_from_document(
                _operation_document(
                    ("T001",),
                    selected_task_ids=None,
                )
            )


def _operation_document(
    task_ids: tuple[str, ...],
    *,
    selected_task_ids: object = _MISSING,
    status: str = "authorized",
) -> dict[str, object]:
    tasks: list[dict[str, object]] = []
    targets: list[dict[str, object]] = []
    for order, task_id in enumerate(task_ids):
        path = f"src/{task_id.lower()}.py"
        tasks.append(
            {
                "order": order,
                "id": task_id,
                "story": None,
                "writes": [path],
            }
        )
        targets.append(
            {
                "path": path,
                "owner": "source",
                "effectiveContextIdentity": f"sha256:context-{task_id}",
            }
        )

    document: dict[str, object] = {
        "schemaVersion": 1,
        "operationId": "legacy-operation",
        "changeId": "001-desktop-text-execution",
        "kind": "implementation",
        "tasks": tasks,
        "authorizedTargets": targets,
        "contractGraphIdentity": "sha256:legacy-graph",
        "gitBaseline": {
            "head": None,
            "dirtyPathStates": [],
        },
        "carriedForward": [],
        "status": status,
    }
    if selected_task_ids is not _MISSING:
        document["selectedTaskIds"] = selected_task_ids
    if status == "verified":
        document["verification"] = {"finalPathStates": []}
    return document


def _init_git(root: Path) -> None:
    subprocess.run(
        ["git", "init", "--quiet"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _write_current(root: Path, document: dict[str, object]) -> None:
    path = root / ".git" / "boundary" / "current.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_contract(root: Path) -> None:
    path = root / "contracts" / "source.contract.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            (
                "---",
                "schema: boundary.contract/v1",
                "id: source",
                "owns:",
                "  - src/**",
                "---",
                "",
                "# Source",
                "",
                "## Invariants",
                "",
                "- Source files remain explicitly owned.",
                "",
            )
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
