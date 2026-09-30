import io
import json
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

from adapter_gate import main
from boundary.authorization import AuthorizationError
from boundary.outcomes import (
    CONTRACT_EVOLUTION_REQUIRED,
    INVALID_ADAPTER_STATE,
    MISSING_EXTERNAL_PREREQUISITE,
    SCOPE_EXPANSION_REQUIRED,
    STALE_AUTHORIZATION,
    VERIFICATION_WRITE_SCOPE_FAILURE,
    classify_lifecycle_codes,
)
from boundary.verification import (
    VerificationDiagnostic,
    VerificationError,
)
from lifecycle_outcome import outcome_for_error
from spec_kit_errors import SpecKitAdapterError


class LifecycleClassificationTests(unittest.TestCase):
    def test_exposes_required_blocking_categories(self):
        cases = (
            (
                ("OPERATION_NOT_VERIFIED",),
                "authorize",
                SCOPE_EXPANSION_REQUIRED,
            ),
            (
                ("OPERATION_KIND_VIOLATION",),
                "authorize",
                CONTRACT_EVOLUTION_REQUIRED,
            ),
            (
                ("AMBIGUOUS_OWNERSHIP",),
                "preflight",
                INVALID_ADAPTER_STATE,
            ),
            (
                ("MISSING_EXTERNAL_PREREQUISITE",),
                "authorize",
                MISSING_EXTERNAL_PREREQUISITE,
            ),
            (
                ("GIT_BASELINE_CHANGED",),
                "verify",
                STALE_AUTHORIZATION,
            ),
        )
        for codes, stage, expected in cases:
            with self.subTest(codes=codes, stage=stage):
                result = classify_lifecycle_codes(codes, stage=stage)
                self.assertEqual(expected, result.category)

    def test_verification_write_failure_carries_transition_hint(self):
        undeclared = classify_lifecycle_codes(
            ("UNDECLARED_WRITE",),
            stage="verify",
        )
        unowned = classify_lifecycle_codes(
            ("UNOWNED_WRITE_TARGET",),
            stage="verify",
        )

        self.assertEqual(
            VERIFICATION_WRITE_SCOPE_FAILURE,
            undeclared.category,
        )
        self.assertEqual(
            SCOPE_EXPANSION_REQUIRED,
            undeclared.required_transition,
        )
        self.assertEqual(
            VERIFICATION_WRITE_SCOPE_FAILURE,
            unowned.category,
        )
        self.assertEqual(
            CONTRACT_EVOLUTION_REQUIRED,
            unowned.required_transition,
        )


class LifecycleOutcomeProjectionTests(unittest.TestCase):
    def test_verification_outcome_preserves_diagnostics_and_identifiers(self):
        error = VerificationError(
            (
                VerificationDiagnostic(
                    "UNDECLARED_WRITE",
                    "write was not authorized",
                    ("src/a.py",),
                ),
                VerificationDiagnostic(
                    "UNOWNED_WRITE_TARGET",
                    "write has no owner",
                    ("docs/state.md",),
                ),
            )
        )

        document = outcome_for_error(
            "verify",
            error,
            change_id="004-change",
            operation_id="operation-1",
        ).to_document()

        self.assertEqual(
            "boundary.lifecycle-outcome/v1",
            document["schema"],
        )
        self.assertEqual(
            VERIFICATION_WRITE_SCOPE_FAILURE,
            document["category"],
        )
        self.assertEqual(
            CONTRACT_EVOLUTION_REQUIRED,
            document["requiredTransition"],
        )
        self.assertEqual("004-change", document["changeId"])
        self.assertEqual("operation-1", document["operationId"])
        self.assertEqual(
            ["UNDECLARED_WRITE", "UNOWNED_WRITE_TARGET"],
            [item["code"] for item in document["diagnostics"]],
        )

    def test_preflight_outcome_never_claims_operation_identity(self):
        error = SpecKitAdapterError(
            "declared target is unowned",
            code="UNOWNED_WRITE_TARGET",
        )

        document = outcome_for_error(
            "preflight",
            error,
            change_id="004-change",
            operation_id="operation-should-not-appear",
        ).to_document()

        self.assertEqual(
            CONTRACT_EVOLUTION_REQUIRED,
            document["category"],
        )
        self.assertEqual("004-change", document["changeId"])
        self.assertNotIn("operationId", document)

    def test_authorization_error_uses_structured_code(self):
        error = AuthorizationError(
            "active operation must be verified",
            code="OPERATION_NOT_VERIFIED",
        )

        document = outcome_for_error(
            "authorize",
            error,
            change_id="004-change",
            operation_id="operation-1",
        ).to_document()

        self.assertEqual(
            SCOPE_EXPANSION_REQUIRED,
            document["category"],
        )
        self.assertEqual(
            "OPERATION_NOT_VERIFIED",
            document["code"],
        )


class AdapterGateFailureOutputTests(unittest.TestCase):
    def test_missing_selection_returns_json_and_human_diagnostic(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        with mock.patch.dict(os.environ, {}, clear=True):
            status = main(
                ("authorize",),
                stdout=stdout,
                stderr=stderr,
            )

        document = json.loads(stdout.getvalue())
        self.assertEqual(2, status)
        self.assertEqual("blocked", document["status"])
        self.assertEqual(
            INVALID_ADAPTER_STATE,
            document["category"],
        )
        self.assertEqual(
            "INVALID_TASK_SELECTION",
            document["code"],
        )
        self.assertIn(
            "requires explicit task ids",
            stderr.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
