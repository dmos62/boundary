import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
SCRIPT_ROOT = REPOSITORY_ROOT / "integration" / "speckit" / "scripts"
for path in (SCRIPT_ROOT, SOURCE_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from adapter_gate import resolve_task_selection
from spec_kit_adapter import SpecKitAdapterError


class SpecKitGateSelectionTests(unittest.TestCase):
    def test_repeated_task_arguments_are_explicit_selection(self):
        selected = resolve_task_selection(
            "authorize",
            ("T009", "T012"),
        )
        self.assertEqual(("T009", "T012"), selected)

    def test_workflow_environment_carries_json_selection(self):
        with mock.patch.dict(
            os.environ,
            {"BOUNDARY_TASK_IDS": '["T009", "T012"]'},
        ):
            selected = resolve_task_selection("authorize", ())

        self.assertEqual(("T009", "T012"), selected)

    def test_authorize_rejects_missing_or_invalid_environment_selection(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                SpecKitAdapterError,
                "requires explicit task ids",
            ):
                resolve_task_selection("authorize", ())

        with mock.patch.dict(
            os.environ,
            {"BOUNDARY_TASK_IDS": "not-json"},
        ):
            with self.assertRaisesRegex(
                SpecKitAdapterError,
                "JSON array",
            ):
                resolve_task_selection("authorize", ())

    def test_verify_does_not_reselect_tasks(self):
        with mock.patch.dict(
            os.environ,
            {"BOUNDARY_TASK_IDS": '["T009"]'},
        ):
            self.assertEqual(
                (),
                resolve_task_selection("verify", ("T012",)),
            )


if __name__ == "__main__":
    unittest.main()
