"""End-to-end native authorization and historical evidence creation."""

from pathlib import Path

from .engine import resolve_contract_scope, resolve_implementation_scope
from boundary.operation.git import capture_git_baseline
from .model import (
    PreChangeError,
    ChangeWriteSet,
    ContractEvolutionWriteSet,
)
from boundary.operation.record import (
    CarriedForwardState,
    GitBaseline,
    OperationRecord,
    contract_evolution_record,
    implementation_record,
)
from boundary.operation.storage import (
    archive_operation,
    check_operation_evidence_persistence,
    read_current_operation,
    write_current_operation,
    require_state_ready,
    prune_predecessors,
    operation_archive_path,
)


def open_implementation_operation(
    repository_root: str | Path,
    change: ChangeWriteSet,
    *,
    selected_task_ids: tuple[str, ...] | None = None,
    operation_id: str | None = None,
) -> OperationRecord:
    """Open one selected implementation unit and persist evidence."""

    require_state_ready(repository_root)
    check_operation_evidence_persistence(repository_root)
    _require_no_open_operation(repository_root)
    authorization = resolve_implementation_scope(
        repository_root,
        change,
        selected_task_ids=selected_task_ids,
    )
    baseline = capture_git_baseline(repository_root)
    predecessor, carried = _carry_forward(
        repository_root,
        baseline,
        change_id=change.change_id,
        kind="implementation",
        targets=authorization.writes,
        selected_task_ids=authorization.selected_task_ids,
    )
    record = implementation_record(
        authorization,
        baseline,
        operation_id=operation_id,
        carried_forward=carried,
    )
    _store_successor(
        repository_root,
        predecessor,
        record,
    )
    return record


def open_contract_operation(
    repository_root: str | Path,
    change: ContractEvolutionWriteSet,
    *,
    operation_id: str | None = None,
) -> OperationRecord:
    """Open contract evolution and persist isolated evidence."""

    require_state_ready(repository_root)
    check_operation_evidence_persistence(repository_root)
    _require_no_open_operation(repository_root)
    authorization = resolve_contract_scope(repository_root, change)
    baseline = capture_git_baseline(repository_root)
    predecessor, carried = _carry_forward(
        repository_root,
        baseline,
        change_id=change.change_id,
        kind="contract-evolution",
        targets=authorization.targets,
        selected_task_ids=(),
    )
    record = contract_evolution_record(
        authorization,
        baseline,
        operation_id=operation_id,
        carried_forward=carried,
    )
    _store_successor(
        repository_root,
        predecessor,
        record,
    )
    return record


def _carry_forward(
    repository_root: str | Path,
    baseline: GitBaseline,
    *,
    change_id: str,
    kind: str,
    targets: tuple[str, ...],
    selected_task_ids: tuple[str, ...],
) -> tuple[
    OperationRecord | None,
    tuple[CarriedForwardState, ...],
]:
    predecessor = read_current_operation(repository_root)
    if predecessor is not None and predecessor.status == "open":
        raise PreChangeError(
            "OPERATION_OPEN: close the current operation before opening another",
            code="OPERATION_OPEN",
        )

    dirty = {
        item.path: item.state
        for item in baseline.dirty_path_states
    }
    dirty_targets = tuple(
        path
        for path in targets
        if path in dirty
    )
    if not dirty_targets:
        return predecessor, ()

    if predecessor is None or predecessor.status != "verified":
        raise PreChangeError(
            "DIRTY_TARGET_NOT_VERIFIED: intended target already contains "
            f"dirty state without predecessor provenance: {dirty_targets[0]}",
            code="DIRTY_TARGET_NOT_VERIFIED",
        )
    if (
        predecessor.change_id != change_id
        or predecessor.kind != kind
        or (kind == "implementation" and predecessor.selected_task_ids != selected_task_ids)
    ):
        raise PreChangeError(
            "DIRTY_TARGET_NOT_VERIFIED: verified predecessor belongs to "
            "a different change or operation kind",
            code="DIRTY_TARGET_NOT_VERIFIED",
        )

    verified = {
        item.path: item.state
        for item in predecessor.verified_final_states
    }
    carried: list[CarriedForwardState] = []
    for path in dirty_targets:
        current_state = dirty[path]
        if verified.get(path) != current_state:
            raise PreChangeError(
                "DIRTY_TARGET_NOT_VERIFIED: intended dirty target does not "
                f"match verified predecessor output: {path}. Restore that "
                "exact verified output before requesting a new operation; "
                "do not commit unverified edits as a workaround",
                code="DIRTY_TARGET_NOT_VERIFIED",
            )
        carried.append(
            CarriedForwardState(
                path=path,
                state=current_state,
                operation_id=predecessor.operation_id,
            )
        )
    return predecessor, tuple(carried)


def _store_successor(
    repository_root: str | Path,
    predecessor: OperationRecord | None,
    record: OperationRecord,
) -> None:
    if record.carried_forward:
        if predecessor is None:
            raise PreChangeError(
                "carry-forward requires a verified predecessor"
            )
        archive_operation(repository_root, predecessor)
    write_current_operation(repository_root, record)
    try:
        _prune_unneeded_predecessors(repository_root, record)
    except (OSError, PreChangeError, ValueError):
        # Pruning is maintenance after the successor has been stored.
        pass


def _require_no_open_operation(repository_root: str | Path) -> None:
    current = read_current_operation(repository_root)
    if current is not None and current.status == "open":
        raise PreChangeError("OPERATION_OPEN: close the current operation first", code="OPERATION_OPEN")


def _prune_unneeded_predecessors(repository_root: str | Path, current: OperationRecord) -> None:
    from boundary.operation.codec import operation_record_from_document
    import json

    keep: set[str] = set()
    pending = [item.operation_id for item in current.carried_forward]
    while pending:
        operation_id = pending.pop()
        if operation_id in keep:
            continue
        path = operation_archive_path(repository_root, operation_id)
        prior = operation_record_from_document(json.loads(path.read_text(encoding="utf-8")))
        keep.add(operation_id)
        pending.extend(item.operation_id for item in prior.carried_forward)
    prune_predecessors(repository_root, keep)
