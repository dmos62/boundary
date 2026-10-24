"""Stable machine-readable lifecycle result vocabulary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

SCOPE_EXPANSION_REQUIRED = "scope-expansion-required"
OPERATION_CLOSURE_REQUIRED = "operation-closure-required"
CONTRACT_EVOLUTION_REQUIRED = "contract-evolution-required"
INVALID_REQUEST_STATE = "invalid-request-state"
MISSING_EXTERNAL_PREREQUISITE = "missing-external-prerequisite"
STALE_OPERATION = "stale-operation"
WRITE_SCOPE_FAILURE = "write-scope-failure"
BOUNDARY_FAILURE = "boundary-failure"

_RESULT_SCHEMA = "boundary.lifecycle-result/v2"

_STALE_CODES = frozenset(
    {
        "CONTRACT_CONTEXT_CHANGED",
        "DIRTY_TARGET_NOT_VERIFIED",
        "GIT_BASELINE_CHANGED",
        "NO_ACTIVE_OPERATION",
        "NO_OPEN_OPERATION",
        "OPERATION_CHANGED",
        "OPERATION_EVIDENCE_INVALID",
    }
)
_INVALID_STATE_CODES = frozenset(
    {
        "AMBIGUOUS_OWNERSHIP",
        "CONTRACT_GRAPH_INVALID",
        "INVALID_REQUEST_STATE",
        "INVALID_TASK_SELECTION",
        "INVALID_WRITE_TARGET",
    }
)
_MISSING_PREREQUISITE_CODES = frozenset(
    {
        "GIT_STATE_UNAVAILABLE",
        "MISSING_EXTERNAL_PREREQUISITE",
        "OPERATION_EVIDENCE_UNAVAILABLE",
        "LEGACY_OPERATION_EVIDENCE",
    }
)


@dataclass(frozen=True, slots=True)
class LifecycleClassification:
    """Stable orchestration-facing classification of a blocking result."""

    category: str
    required_transition: str | None = None


@dataclass(frozen=True, slots=True)
class LifecycleDiagnostic:
    """One machine-readable diagnostic contributing to a lifecycle result."""

    code: str
    message: str
    paths: tuple[str, ...] = ()

    def to_document(self) -> dict[str, object]:
        value: dict[str, object] = {
            "code": self.code,
            "message": self.message,
        }
        if self.paths:
            value["paths"] = list(self.paths)
        return value


@dataclass(frozen=True, slots=True)
class LifecycleSuccess:
    """One concise successful lifecycle result."""

    stage: str
    status: str
    operation_id: str
    change_id: str
    selected_task_ids: tuple[str, ...] = ()
    allowed_targets: tuple[str, ...] = ()

    def to_document(self) -> dict[str, object]:
        document: dict[str, object] = {
            "schema": _RESULT_SCHEMA,
            "status": self.status,
            "stage": self.stage,
            "operationId": self.operation_id,
            "changeId": self.change_id,
            "diagnostics": [],
        }
        if self.selected_task_ids:
            document["selectedTaskIds"] = list(self.selected_task_ids)
        if self.allowed_targets:
            document["allowedTargets"] = list(self.allowed_targets)
        return document


@dataclass(frozen=True, slots=True)
class LifecycleOutcome:
    """One stable blocked lifecycle result for external orchestration."""

    stage: str
    category: str
    code: str
    message: str
    change_id: str | None = None
    operation_id: str | None = None
    required_transition: str | None = None
    diagnostics: tuple[LifecycleDiagnostic, ...] = ()

    def to_document(self) -> dict[str, object]:
        document: dict[str, object] = {
            "schema": _RESULT_SCHEMA,
            "status": "blocked",
            "stage": self.stage,
            "category": self.category,
            "code": self.code,
            "message": self.message,
            "diagnostics": [
                item.to_document()
                for item in self.diagnostics
            ],
        }
        if self.change_id is not None:
            document["changeId"] = self.change_id
        if self.operation_id is not None:
            document["operationId"] = self.operation_id
        if self.required_transition is not None:
            document["requiredTransition"] = self.required_transition
        return document


def classify_lifecycle_codes(
    codes: Sequence[str],
    *,
    stage: str,
    operation_kind: str = "implementation",
) -> LifecycleClassification:
    """Classify structured diagnostic codes without parsing human prose."""

    present = frozenset(code for code in codes if code)

    if present & _MISSING_PREREQUISITE_CODES:
        return LifecycleClassification(MISSING_EXTERNAL_PREREQUISITE)

    if (
        "OPERATION_KIND_VIOLATION" in present
        and operation_kind == "implementation"
    ):
        return LifecycleClassification(CONTRACT_EVOLUTION_REQUIRED)

    if stage == "post-change" and present & {
        "UNDECLARED_WRITE",
        "UNOWNED_WRITE_TARGET",
    }:
        transition = (
            CONTRACT_EVOLUTION_REQUIRED
            if "UNOWNED_WRITE_TARGET" in present
            else SCOPE_EXPANSION_REQUIRED
        )
        return LifecycleClassification(
            WRITE_SCOPE_FAILURE,
            required_transition=transition,
        )

    if "OPERATION_OPEN" in present:
        return LifecycleClassification(OPERATION_CLOSURE_REQUIRED)

    if present & _STALE_CODES:
        return LifecycleClassification(STALE_OPERATION)

    if "UNOWNED_WRITE_TARGET" in present:
        return LifecycleClassification(CONTRACT_EVOLUTION_REQUIRED)

    if present & _INVALID_STATE_CODES:
        return LifecycleClassification(INVALID_REQUEST_STATE)

    return LifecycleClassification(BOUNDARY_FAILURE)
