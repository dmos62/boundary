"""Generic, structured Boundary lifecycle command handlers."""

import json
from pathlib import Path
from typing import TextIO

from boundary.operation.storage import read_current_operation
from boundary.outcomes import LifecycleDiagnostic, LifecycleOutcome, LifecycleSuccess, classify_lifecycle_codes
from boundary.pre_change.model import PreChangeError, ContractEvolutionWriteSet, WriteSetError
from boundary.pre_change.service import open_contract_operation, open_implementation_operation
from boundary.post_change.errors import PostChangeError
from boundary.post_change.service import abandon_operation, close_verified_operation
from boundary.request import read_request


def _print(value: dict[str, object], output: TextIO) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False), file=output)


def _blocked(stage: str, error: Exception, root: Path, output: TextIO) -> int:
    if isinstance(error, PostChangeError) and error.diagnostics:
        diagnostics = tuple(LifecycleDiagnostic(item.code, item.message, item.paths) for item in error.diagnostics)
    else:
        code = getattr(error, "code", None) or ("INVALID_REQUEST" if isinstance(error, WriteSetError) else "BOUNDARY_FAILURE")
        diagnostics = (LifecycleDiagnostic(code, str(error)),)
    current = None
    try:
        current = read_current_operation(root)
    except PreChangeError:
        pass
    classification = classify_lifecycle_codes(tuple(item.code for item in diagnostics), stage=stage, operation_kind=current.kind if current else "implementation")
    _print(LifecycleOutcome(
        stage=stage, category=classification.category,
        code=diagnostics[0].code, message=str(error),
        operation_id=current.operation_id if current else None,
        change_id=current.change_id if current else None,
        required_transition=classification.required_transition,
        diagnostics=diagnostics,
    ).to_document(), output)
    return 2


def run_pre_change(root: Path, request: str, stdin: TextIO, output: TextIO) -> int:
    try:
        change, selection = read_request(request, stdin)
        record = open_implementation_operation(root, change, selected_task_ids=selection)
    except (PreChangeError, WriteSetError, OSError, ValueError) as exc:
        return _blocked("pre-change", exc, root, output)
    _print(LifecycleSuccess(
        stage="pre-change", status=record.status,
        operation_id=record.operation_id, change_id=record.change_id,
        selected_task_ids=record.selected_task_ids,
        allowed_targets=tuple(item.path for item in record.allowed_targets),
    ).to_document(), output)
    return 0


def run_contract_pre_change(root: Path, change_id: str, targets: tuple[str, ...], output: TextIO) -> int:
    try:
        record = open_contract_operation(root, ContractEvolutionWriteSet(change_id, targets))
    except (PreChangeError, WriteSetError, OSError, ValueError) as exc:
        return _blocked("pre-change", exc, root, output)
    _print(LifecycleSuccess(
        stage="pre-change", status=record.status,
        operation_id=record.operation_id, change_id=record.change_id,
        allowed_targets=tuple(item.path for item in record.allowed_targets),
    ).to_document(), output)
    return 0


def run_post_change(root: Path, output: TextIO) -> int:
    try:
        record = close_verified_operation(root)
    except (PostChangeError, PreChangeError, OSError, ValueError) as exc:
        return _blocked("post-change", exc, root, output)
    _print(LifecycleSuccess(
        stage="post-change", status=record.status,
        operation_id=record.operation_id, change_id=record.change_id,
    ).to_document(), output)
    return 0


def run_post_abandon(root: Path, output: TextIO) -> int:
    try:
        record = abandon_operation(root)
    except (PostChangeError, PreChangeError, OSError, ValueError) as exc:
        return _blocked("post-abandon", exc, root, output)
    _print(LifecycleSuccess(
        stage="post-abandon", status=record.status,
        operation_id=record.operation_id, change_id=record.change_id,
    ).to_document(), output)
    return 0
