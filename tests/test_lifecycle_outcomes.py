"""Tests for stable lifecycle outcomes from the installed Spec Kit adapter."""

from __future__ import annotations

import unittest

from boundary.authorization import AuthorizationError
from boundary.outcomes import (
    CONTRACT_EVOLUTION_REQUIRED,
    INVALID_ADAPTER_STATE,
    MISSING_EXTERNAL_PREREQUISITE,
    VERIFICATION_WRITE_SCOPE_FAILURE,
)
from boundary.verification import VerificationDiagnostic, VerificationError
from boundary_host.errors import SpecKitAdapterError
from boundary_host.outcomes import outcome_for_error


class LifecycleOutcomeTests(unittest.TestCase):
    def test_invalid_task_selection_is_adapter_state(self) -> None:
        outcome = outcome_for_error(
            "authorize",
            SpecKitAdapterError(
                "task selection is invalid",
                code="INVALID_TASK_SELECTION",
            ),
            change_id="001-example",
        )
        self.assertEqual(INVALID_ADAPTER_STATE, outcome.category)
        self.assertEqual("INVALID_TASK_SELECTION", outcome.code)
        self.assertEqual("001-example", outcome.change_id)

    def test_missing_prerequisite_is_distinct(self) -> None:
        outcome = outcome_for_error(
            "authorize",
            AuthorizationError(
                "Git is unavailable",
                code="GIT_STATE_UNAVAILABLE",
            ),
        )
        self.assertEqual(MISSING_EXTERNAL_PREREQUISITE, outcome.category)
        self.assertEqual("GIT_STATE_UNAVAILABLE", outcome.code)

    def test_unowned_verification_write_requires_contract_transition(self) -> None:
        error = VerificationError(
            VerificationDiagnostic(
                code="UNOWNED_WRITE_TARGET",
                message="write has no owner",
                paths=("specs/CONTINUATION.md",),
            )
        )
        outcome = outcome_for_error(
            "verify",
            error,
            change_id="003-example",
            operation_id="operation-1",
        )
        self.assertEqual(VERIFICATION_WRITE_SCOPE_FAILURE, outcome.category)
        self.assertEqual(CONTRACT_EVOLUTION_REQUIRED, outcome.required_transition)
        self.assertEqual(
            ["specs/CONTINUATION.md"],
            outcome.to_document()["diagnostics"][0]["paths"],
        )


if __name__ == "__main__":
    unittest.main()
