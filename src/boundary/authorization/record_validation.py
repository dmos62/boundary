"""Validation helpers for native Boundary operation records."""

import re

from boundary.repository import normalize_repo_path

_OPERATION_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


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
