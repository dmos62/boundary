"""Revision-only downstream Boundary lock parsing and writing."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import tempfile

_SCHEMA = "boundary.lock/v2"
_REVISION_RE = re.compile(r"^[0-9a-f]{40}$")


class BoundaryLockError(ValueError):
    """Raised when downstream Boundary source identity is invalid."""


@dataclass(frozen=True, slots=True)
class BoundaryLock:
    """One exact Boundary Git revision adopted by a downstream project."""

    revision: str

    def __post_init__(self) -> None:
        if not isinstance(self.revision, str):
            raise BoundaryLockError("source revision must be a string")

        revision = self.revision.lower()
        if _REVISION_RE.fullmatch(revision) is None:
            raise BoundaryLockError(
                "source revision must be a 40-character Git commit id"
            )
        object.__setattr__(self, "revision", revision)

    def to_document(self) -> dict[str, object]:
        """Return the stable downstream lock document."""

        return {
            "schema": _SCHEMA,
            "source": {
                "revision": self.revision,
            },
        }


def load_lock(path: str | Path) -> BoundaryLock:
    """Load and strictly validate one committed Boundary lock."""

    lock_path = Path(path)
    try:
        value = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BoundaryLockError(f"Boundary lock is invalid JSON: {exc}") from exc

    if not isinstance(value, dict):
        raise BoundaryLockError("Boundary lock must be a JSON object")
    if set(value) != {"schema", "source"}:
        raise BoundaryLockError(
            "Boundary lock must contain only schema and source"
        )
    if value["schema"] != _SCHEMA:
        raise BoundaryLockError(f"Boundary lock schema must be {_SCHEMA!r}")

    source = value["source"]
    if not isinstance(source, dict):
        raise BoundaryLockError("Boundary lock source must be an object")
    if set(source) != {"revision"}:
        raise BoundaryLockError(
            "Boundary lock source must contain only revision"
        )
    if not isinstance(source["revision"], str):
        raise BoundaryLockError("Boundary lock source revision must be a string")

    return BoundaryLock(revision=source["revision"])


def write_lock(path: str | Path, lock: BoundaryLock) -> None:
    """Atomically replace a downstream Boundary lock."""

    output = Path(path)
    rendered = (
        json.dumps(
            lock.to_document(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=output.parent,
            prefix=output.name + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(rendered)
            temporary = Path(handle.name)
        temporary.replace(output)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
