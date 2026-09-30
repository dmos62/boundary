"""Machine-readable blocking outcomes for the Spec Kit adapter gate."""

from __future__ import annotations

from boundary.authorization import AuthorizationError
from boundary.outcomes import (
    LifecycleDiagnostic,
    LifecycleOutcome,
    classify_lifecycle_codes,
)
from boundary.verification import VerificationError

from spec_kit_errors import SpecKitAdapterError


def outcome_for_error(
    stage: str,
    error: Exception,
    *,
    change_id: str | None = None,
    operation_id: str | None = None,
) -> LifecycleOutcome:
    """Project one blocking adapter error without parsing diagnostic prose."""

    diagnostics = _diagnostics(error)
    codes = tuple(item.code for item in diagnostics)
    classification = classify_lifecycle_codes(
        codes,
        stage=stage,
        operation_kind="implementation",
    )
    return LifecycleOutcome(
        stage=stage,
        category=classification.category,
        code=codes[0],
        message=str(error),
        change_id=change_id,
        operation_id=None if stage == "preflight" else operation_id,
        required_transition=classification.required_transition,
        diagnostics=diagnostics,
    )


def _diagnostics(error: Exception) -> tuple[LifecycleDiagnostic, ...]:
    if isinstance(error, VerificationError) and error.diagnostics:
        return tuple(
            LifecycleDiagnostic(
                code=item.code,
                message=item.message,
                paths=item.paths,
            )
            for item in error.diagnostics
        )

    if isinstance(error, SpecKitAdapterError):
        code = error.code
    elif isinstance(error, AuthorizationError):
        code = error.code or "AUTHORIZATION_FAILED"
    elif isinstance(error, OSError):
        code = "MISSING_EXTERNAL_PREREQUISITE"
    elif isinstance(error, ValueError):
        code = "INVALID_ADAPTER_STATE"
    else:
        code = "BOUNDARY_FAILURE"

    return (
        LifecycleDiagnostic(
            code=code,
            message=str(error),
        ),
    )
