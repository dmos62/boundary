"""Git-derived native authorization verification and epoch closure."""

from pathlib import Path

from boundary.pre_change.model import PreChangeError
from boundary.operation.record import OperationRecord
from boundary.operation.storage import (
    OPERATION_EVIDENCE_UNAVAILABLE,
    check_operation_evidence_persistence,
    require_state_ready,
    read_current_operation,
    write_current_operation,
)

from .checks import (
    diagnostic,
    check_allowed_writes,
)
from .errors import PostChangeError
from .git import capture_git_delta
from .model import PostChangeDiagnostic, PostChangeResult


def check_operation_writes(
    repository_root: str | Path,
    *,
    operation_id: str | None = None,
) -> PostChangeResult:
    """Compare Git writes with one open operation record."""

    try:
        require_state_ready(repository_root)
        check_operation_evidence_persistence(repository_root)
    except PreChangeError as exc:
        raise _post_change_error_from_pre_change(exc) from exc

    current = _load_current(repository_root)
    _require_operation(current, operation_id)
    if current.status != "open":
        raise PostChangeError(diagnostic("NO_OPEN_OPERATION", "no open Boundary operation is available"))

    try:
        delta = capture_git_delta(
            repository_root,
            current.git_baseline,
        )
    except PreChangeError as exc:
        raise PostChangeError(
            diagnostic("GIT_STATE_UNAVAILABLE", str(exc))
        ) from exc

    diagnostics: list[PostChangeDiagnostic] = []
    if delta.head != current.git_baseline.head:
        diagnostics.append(
            diagnostic(
                "GIT_BASELINE_CHANGED",
                "Git HEAD changed after pre-change; the operation cannot close against its baseline",
            )
        )
        return PostChangeResult(
            operation=current,
            dirty_path_states=delta.dirty_path_states,
            diagnostics=tuple(diagnostics),
        )

    checked = delta.actual_paths
    diagnostics.extend(
        check_allowed_writes(
            repository_root,
            current,
            checked,
        )
    )
    return PostChangeResult(
        operation=current,
        actual_paths=delta.actual_paths,
        checked_writes=checked,
        dirty_path_states=delta.dirty_path_states,
        diagnostics=tuple(diagnostics),
    )


def close_verified_operation(
    repository_root: str | Path,
    *,
    operation_id: str | None = None,
) -> OperationRecord:
    """Check actual writes, then close the open operation as verified."""

    result = check_operation_writes(
        repository_root,
        operation_id=operation_id,
    )
    current = result.operation
    if current.status != "open":
        raise PostChangeError(diagnostic("NO_OPEN_OPERATION", "no open Boundary operation is available"))
    if result.blocking:
        raise PostChangeError(result.diagnostics)

    target_paths = {
        target.path
        for target in current.allowed_targets
    }
    final_states = tuple(
        state
        for state in result.dirty_path_states
        if state.path in target_paths
    )
    verified = current.mark_verified(final_states)
    try:
        write_current_operation(repository_root, verified)
    except PreChangeError as exc:
        raise _post_change_error_from_pre_change(exc) from exc
    return verified


def _load_current(
    repository_root: str | Path,
) -> OperationRecord:
    try:
        current = read_current_operation(repository_root)
    except PreChangeError as exc:
        raise PostChangeError(
            diagnostic(exc.code or "OPERATION_EVIDENCE_INVALID", str(exc))
        ) from exc
    if current is None:
        raise PostChangeError(
            diagnostic(
                "NO_ACTIVE_OPERATION",
                "no open Boundary operation is available",
            )
        )
    return current


def _require_operation(
    current: OperationRecord,
    operation_id: str | None,
) -> None:
    if operation_id is not None and current.operation_id != operation_id:
        raise PostChangeError(
            diagnostic(
                "OPERATION_CHANGED",
                "operation changed before post-change could finish",
            )
        )


def _post_change_error_from_pre_change(
    error: PreChangeError,
) -> PostChangeError:
    return PostChangeError(
        diagnostic(
            error.code or OPERATION_EVIDENCE_UNAVAILABLE,
            str(error),
        )
    )


def abandon_operation(repository_root: str | Path) -> OperationRecord:
    """Close an open operation without checking or altering project files."""
    current = _load_current(repository_root)
    if current.status != "open":
        raise PostChangeError(diagnostic("NO_OPEN_OPERATION", "no open Boundary operation is available"))
    abandoned = current.mark_abandoned()
    try:
        write_current_operation(repository_root, abandoned)
    except PreChangeError as exc:
        raise _post_change_error_from_pre_change(exc) from exc
    return abandoned
