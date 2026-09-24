"""Generated-state and provenance handling for downstream consumers."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

from consumer_lock import BoundaryLock

PROVENANCE = Path(".specify") / "boundary-runtime" / "source-lock.json"
EXCLUDE_BEGIN = "# BEGIN Boundary generated state"
EXCLUDE_END = "# END Boundary generated state"
GENERATED_EXCLUDES = (
    "/.agents/skills/boundary-scope/",
    "/.agents/skills/boundary-implement/",
    "/.agents/skills/boundary-contracts/",
    "/.agents/skills/speckit-boundary-authorize/",
    "/.agents/skills/speckit-boundary-verify/",
    "/.specify/boundary-runtime/",
    "/.specify/extensions/boundary/",
    "/.specify/presets/boundary/",
    "/.specify/workflows/overlays/speckit/boundary.yml",
)


class ConsumerStateError(RuntimeError):
    """Raised when generated consumer state cannot be read or maintained."""


def write_provenance(root: Path, lock: BoundaryLock) -> None:
    output = root / PROVENANCE
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            lock.to_document(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def require_provenance(root: Path, lock: BoundaryLock) -> None:
    path = root / PROVENANCE
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConsumerStateError(
            "installed Boundary source provenance is missing or invalid"
        ) from exc
    if value != lock.to_document():
        raise ConsumerStateError(
            "installed Boundary source does not match boundary.lock.json"
        )


def update_local_excludes(root: Path, *, enabled: bool) -> None:
    path = _git_exclude_path(root)
    try:
        existing = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        existing = []

    lines = _without_managed_excludes(existing)
    while lines and not lines[-1]:
        lines.pop()

    if enabled:
        if lines:
            lines.append("")
        lines.append(EXCLUDE_BEGIN)
        lines.extend(GENERATED_EXCLUDES)
        lines.append(EXCLUDE_END)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(lines) + ("\n" if lines else ""),
        encoding="utf-8",
    )


def require_local_excludes(root: Path) -> None:
    path = _git_exclude_path(root)
    try:
        lines = set(path.read_text(encoding="utf-8").splitlines())
    except OSError as exc:
        raise ConsumerStateError(
            "Boundary generated-state Git exclusions are missing"
        ) from exc

    required = {
        EXCLUDE_BEGIN,
        EXCLUDE_END,
        *GENERATED_EXCLUDES,
    }
    if not required.issubset(lines):
        raise ConsumerStateError(
            "Boundary generated-state Git exclusions are missing or stale"
        )


def _git_exclude_path(root: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", "info/exclude"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        detail = " ".join((result.stderr or result.stdout).split())
        raise ConsumerStateError(
            "could not determine Git local exclude file"
            + (f": {detail}" if detail else "")
        )
    path = Path(result.stdout.strip())
    if not path.is_absolute():
        path = root / path
    return path


def _without_managed_excludes(lines: list[str]) -> list[str]:
    result: list[str] = []
    inside = False
    for line in lines:
        if line == EXCLUDE_BEGIN:
            inside = True
            continue
        if line == EXCLUDE_END:
            inside = False
            continue
        if not inside:
            result.append(line)
    return result
