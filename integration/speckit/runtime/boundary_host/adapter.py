"""Concrete Spec Kit change-system projection for installed Boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from boundary.authorization import (
    AuthorizationHandoff,
    ChangeWriteSet,
    OperationRecord,
    WriteSetError,
    authorize_implementation_operation,
    read_authorization_handoff,
    read_current_operation,
)
from boundary.context import TargetContext, resolve_target_context
from boundary.contracts import (
    ContractGraphError,
    ContractOwnershipError,
    ContractParseError,
    load_contract_graph,
)
from boundary.verification import finalize_operation_verification

from .errors import SpecKitAdapterError
from .tasks import parse_tasks


@dataclass(frozen=True, slots=True)
class SpecKitAuthorizationStatus:
    """Read-only Boundary handoff plus its relationship to the active feature."""

    handoff: AuthorizationHandoff | None
    change_matches_active_feature: bool | None


def project_change(
    root: Path,
    feature_dir: Path,
) -> ChangeWriteSet:
    """Project one active feature into Boundary's normalized change model."""

    del root
    task_path = feature_dir / "tasks.md"
    try:
        source = task_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SpecKitAdapterError(
            f"active Spec Kit task file is unavailable: {task_path}: {exc}",
            code="MISSING_EXTERNAL_PREREQUISITE",
        ) from exc

    try:
        return ChangeWriteSet(
            change_id=feature_dir.name,
            tasks=parse_tasks(source),
        )
    except WriteSetError as exc:
        raise SpecKitAdapterError(
            f"active Spec Kit task scope is invalid: {exc}"
        ) from exc


def preflight_declared_scope(
    root: Path,
    feature_dir: Path,
) -> tuple[TargetContext, ...]:
    """Inspect the complete declared change scope without authorizing it."""

    change = project_change(root, feature_dir)
    try:
        graph = load_contract_graph(root)
        contexts = tuple(
            resolve_target_context(graph, target)
            for target in change.writes
        )
    except ContractOwnershipError as exc:
        raise SpecKitAdapterError(
            "declared-scope preflight found ambiguous ownership: "
            f"{exc}",
            code="AMBIGUOUS_OWNERSHIP",
        ) from exc
    except (ContractParseError, ContractGraphError) as exc:
        raise SpecKitAdapterError(
            "declared-scope preflight could not resolve Boundary target "
            f"context: {exc}",
            code="CONTRACT_GRAPH_INVALID",
        ) from exc

    unowned = tuple(
        context.target_path
        for context in contexts
        if context.owner_id is None
    )
    if unowned:
        raise SpecKitAdapterError(
            "declared-scope preflight found unowned declared targets: "
            + ", ".join(unowned),
            code="UNOWNED_WRITE_TARGET",
        ) from exc
    return contexts


def status_feature(
    root: Path,
    feature_dir: Path,
) -> SpecKitAuthorizationStatus:
    """Return current Boundary handoff and active-feature match state."""

    handoff = read_authorization_handoff(root)
    return SpecKitAuthorizationStatus(
        handoff=handoff,
        change_matches_active_feature=(
            None
            if handoff is None
            else handoff.change_id == feature_dir.name
        ),
    )


def authorize_feature(
    root: Path,
    feature_dir: Path,
    selected_task_ids: tuple[str, ...] | None = None,
) -> OperationRecord:
    """Fresh-authorize one selected unit from the active feature."""

    try:
        return authorize_implementation_operation(
            root,
            project_change(root, feature_dir),
            selected_task_ids=selected_task_ids,
        )
    except WriteSetError as exc:
        raise SpecKitAdapterError(
            f"invalid implementation task selection: {exc}",
            code="INVALID_TASK_SELECTION",
        ) from exc


def verify_feature(
    root: Path,
    feature_dir: Path,
) -> OperationRecord:
    """Verify and close the active feature's Boundary operation."""

    current = read_current_operation(root)
    if current is None:
        raise SpecKitAdapterError(
            "no active Boundary operation is available for this feature",
            code="NO_ACTIVE_OPERATION",
        )
    if current.kind != "implementation":
        raise SpecKitAdapterError(
            "active Boundary operation is not an implementation operation",
            code="OPERATION_CHANGED",
        )
    if current.change_id != feature_dir.name:
        raise SpecKitAdapterError(
            "active Boundary operation belongs to another Spec Kit feature",
            code="OPERATION_CHANGED",
        )

    relative = feature_dir.relative_to(root).as_posix()
    return finalize_operation_verification(
        root,
        operation_id=current.operation_id,
        classify_path=path_classifier(relative),
    )


def path_classifier(
    feature_path: str,
) -> Callable[[str], str]:
    """Return deterministic Spec Kit bookkeeping classification."""

    feature_root = feature_path.rstrip("/")

    def classify(path: str) -> str:
        if path == ".specify" or path.startswith(".specify/"):
            return "change-system"
        if path == feature_root or path.startswith(f"{feature_root}/"):
            return "change-system"
        return "ordinary"

    return classify
