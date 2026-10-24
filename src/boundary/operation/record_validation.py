"""Validation helpers for native Boundary operation records."""

import re
from typing import Protocol

from boundary.repository import normalize_repo_path

_OPERATION_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class _TaskEvidence(Protocol):
    order: int
    writes: tuple[str, ...]


class _ImplementationTargetEvidence(Protocol):
    path: str
    owner: str | None
    effective_context_identity: str | None


def validate_path(path: str) -> None:
    """Require one canonical repository-relative operation path."""

    normalized = normalize_repo_path(path)
    if normalized != path:
        raise ValueError(f"operation path must be canonical: {path!r}")


def validate_nonempty(value: str, label: str) -> None:
    """Require a non-empty string value."""

    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")


def validate_operation_id(value: str) -> None:
    """Require one filesystem-safe operation identifier."""

    if not isinstance(value, str) or not _OPERATION_ID_RE.fullmatch(value):
        raise ValueError("operation id contains unsupported characters")


def validate_unique_paths(values: tuple[object, ...], label: str) -> None:
    """Require path-bearing evidence entries to name unique paths."""

    paths = [getattr(item, "path") for item in values]
    if len(paths) != len(set(paths)):
        raise ValueError(f"{label}s must be unique")


def validate_implementation_record_authority(
    tasks: tuple[_TaskEvidence, ...],
    targets: tuple[_ImplementationTargetEvidence, ...],
) -> None:
    """Require persisted implementation authority to prove its task write union."""

    orders = tuple(task.order for task in tasks)
    if len(orders) != len(set(orders)) or orders != tuple(sorted(orders)):
        raise ValueError(
            "implementation task evidence must preserve unique canonical task order"
        )

    declared_paths = tuple(
        path
        for task in tasks
        for path in task.writes
    )
    if not declared_paths:
        raise ValueError(
            "implementation selected task evidence must declare at least one write target"
        )

    target_paths = tuple(target.path for target in targets)
    if target_paths != declared_paths:
        raise ValueError(
            "implementation authorized targets must exactly match selected task writes"
        )

    for target in targets:
        if (
            target.owner is None
            or target.effective_context_identity is None
        ):
            raise ValueError(
                "implementation authorized target must include owner and "
                f"effective context identity: {target.path}"
            )
