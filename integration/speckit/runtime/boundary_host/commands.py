"""Installed Boundary command handlers for the concrete Spec Kit adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Sequence, TextIO

from boundary.authorization import (
    AuthorizationError,
    read_current_operation,
)
from boundary.outcomes import LifecycleSuccess
from boundary.verification import VerificationError

from .adapter import authorize_feature, verify_feature
from .discovery import active_feature
from .errors import SpecKitAdapterError
from .outcomes import outcome_for_error

_TASK_SELECTION_ENV = "BOUNDARY_TASK_IDS"


def run_authorize(
    root: Path,
    task_ids: str | Sequence[str],
    output: TextIO,
    errors: TextIO,
) -> int:
    """Authorize one explicitly selected Spec Kit implementation unit."""

    try:
        selected = _resolve_task_selection(task_ids)
        feature_dir, _ = active_feature(root)
        record = authorize_feature(root, feature_dir, selected)
    except _BLOCKING_ERRORS as exc:
        return _render_error(
            root,
            "authorize",
            exc,
            output,
            errors,
        )

    _render_json(
        LifecycleSuccess(
            stage="authorize",
            status=record.status,
            operation_id=record.operation_id,
            change_id=record.change_id,
            selected_task_ids=record.selected_task_ids,
            authorized_targets=tuple(
                target.path
                for target in record.authorized_targets
            ),
        ).to_document(),
        output,
    )
    return 0


def run_verify(
    root: Path,
    output: TextIO,
    errors: TextIO,
) -> int:
    """Verify the active Spec Kit implementation operation."""

    try:
        feature_dir, _ = active_feature(root)
        record = verify_feature(root, feature_dir)
    except _BLOCKING_ERRORS as exc:
        return _render_error(
            root,
            "verify",
            exc,
            output,
            errors,
        )

    _render_json(
        LifecycleSuccess(
            stage="verify",
            status=record.status,
            operation_id=record.operation_id,
            change_id=record.change_id,
            selected_task_ids=record.selected_task_ids,
        ).to_document(),
        output,
    )
    return 0


_BLOCKING_ERRORS = (
    AuthorizationError,
    VerificationError,
    SpecKitAdapterError,
    OSError,
    ValueError,
)


def _resolve_task_selection(
    task_ids: str | Sequence[str],
) -> tuple[str, ...]:
    supplied = (
        (task_ids,)
        if isinstance(task_ids, str)
        else tuple(task_ids)
    )
    if supplied:
        if any(
            not isinstance(item, str) or not item.strip()
            for item in supplied
        ):
            raise SpecKitAdapterError(
                "implementation task selection must contain only "
                "non-empty task ids",
                code="INVALID_TASK_SELECTION",
            )
        return supplied

    raw = os.environ.get(_TASK_SELECTION_ENV)
    if raw is None or not raw.strip():
        raise SpecKitAdapterError(
            "implementation authorization requires explicit task ids; "
            "pass task ids positionally or, for workflow integration, "
            "set BOUNDARY_TASK_IDS to a JSON array",
            code="INVALID_TASK_SELECTION",
        )
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpecKitAdapterError(
            "BOUNDARY_TASK_IDS must contain a JSON array of task ids",
            code="INVALID_TASK_SELECTION",
        ) from exc
    if (
        not isinstance(value, list)
        or not value
        or any(
            not isinstance(item, str) or not item.strip()
            for item in value
        )
    ):
        raise SpecKitAdapterError(
            "BOUNDARY_TASK_IDS must contain a non-empty JSON array "
            "of non-empty task ids",
            code="INVALID_TASK_SELECTION",
        )
    return tuple(value)


def _render_error(
    root: Path,
    stage: str,
    error: Exception,
    output: TextIO,
    errors: TextIO,
) -> int:
    change_id: str | None = None
    try:
        feature_dir, _ = active_feature(root)
        change_id = feature_dir.name
    except _BLOCKING_ERRORS:
        pass

    outcome = outcome_for_error(
        stage,
        error,
        change_id=change_id,
        operation_id=_current_operation_id(root),
    )
    _render_json(outcome.to_document(), output)
    print(f"boundary Spec Kit adapter: {error}", file=errors)
    return 2


def _current_operation_id(root: Path) -> str | None:
    try:
        current = read_current_operation(root)
    except (AuthorizationError, OSError, ValueError):
        return None
    return None if current is None else current.operation_id


def _render_json(
    value: dict[str, object],
    output: TextIO,
) -> None:
    print(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        file=output,
    )
