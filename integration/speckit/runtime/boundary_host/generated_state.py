"""Boundary-owned generated-state exclusion and legacy cleanup."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from .errors import IntegrationError

EXCLUDE_BEGIN = "# BEGIN Boundary generated state"
EXCLUDE_END = "# END Boundary generated state"
GENERATED_EXCLUDES = (
    "/.agents/skills/boundary-scope/",
    "/.agents/skills/boundary-implement/",
    "/.agents/skills/boundary-contracts/",
    "/.agents/skills/speckit-boundary-authorize/",
    "/.agents/skills/speckit-boundary-verify/",
    "/.specify/extensions/boundary/",
    "/.specify/presets/boundary/",
    "/.specify/workflows/overlays/speckit/boundary.yml",
)
LEGACY_GENERATED_PATHS = (
    Path(".boundary"),
    Path(".specify") / "boundary-runtime",
)


def cleanup_legacy_generated_state(root: Path) -> None:
    """Remove generated runtime and launcher state from the retired model."""

    for relative in LEGACY_GENERATED_PATHS:
        path = root / relative
        try:
            if path.is_symlink() or path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except OSError as exc:
            raise IntegrationError(
                f"could not remove legacy Boundary generated state: {relative}: {exc}"
            ) from exc


def require_no_legacy_generated_state(root: Path) -> None:
    """Fail when retired copied-runtime or launcher state remains."""

    for relative in LEGACY_GENERATED_PATHS:
        if (root / relative).exists() or (root / relative).is_symlink():
            raise IntegrationError(
                f"legacy Boundary generated state is still present: {relative}"
            )


def update_local_excludes(root: Path, *, enabled: bool) -> None:
    """Replace Boundary's managed current-worktree Git exclude block."""

    path = _git_exclude_path(root)
    try:
        existing = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        existing = []
    except OSError as exc:
        raise IntegrationError(
            f"could not read Git local exclude file: {exc}"
        ) from exc

    lines = _without_managed_excludes(existing)
    while lines and not lines[-1]:
        lines.pop()

    if enabled:
        if lines:
            lines.append("")
        lines.append(EXCLUDE_BEGIN)
        lines.extend(GENERATED_EXCLUDES)
        lines.append(EXCLUDE_END)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(lines) + ("\n" if lines else ""),
            encoding="utf-8",
        )
    except OSError as exc:
        raise IntegrationError(
            f"could not update Git local exclude file: {exc}"
        ) from exc


def require_local_excludes(root: Path) -> None:
    """Require the exact Boundary-owned generated-state exclude block."""

    path = _git_exclude_path(root)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise IntegrationError(
            "Boundary generated-state Git exclusions are missing"
        ) from exc

    span = _managed_exclude_span(lines)
    if span is None:
        raise IntegrationError(
            "Boundary generated-state Git exclusions are missing or stale"
        )

    start, end = span
    if tuple(lines[start + 1 : end]) != GENERATED_EXCLUDES:
        raise IntegrationError(
            "Boundary generated-state Git exclusions are missing or stale"
        )


def _git_exclude_path(root: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-path", "info/exclude"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise IntegrationError("required command not found: git") from exc
    except OSError as exc:
        raise IntegrationError(f"Git could not be executed: {exc}") from exc

    if result.returncode != 0 or not result.stdout.strip():
        detail = " ".join((result.stderr or result.stdout).split())
        raise IntegrationError(
            "could not determine Git local exclude file"
            + (f": {detail}" if detail else "")
        )
    path = Path(result.stdout.strip())
    return path if path.is_absolute() else root / path


def _without_managed_excludes(lines: list[str]) -> list[str]:
    span = _managed_exclude_span(lines)
    if span is None:
        return list(lines)

    start, end = span
    return [*lines[:start], *lines[end + 1 :]]


def _managed_exclude_span(
    lines: list[str],
) -> tuple[int, int] | None:
    start: int | None = None
    end: int | None = None

    for index, line in enumerate(lines):
        if line == EXCLUDE_BEGIN:
            if start is not None:
                raise IntegrationError(
                    "Boundary generated-state Git exclusion block is malformed"
                )
            start = index
        elif line == EXCLUDE_END:
            if start is None or end is not None:
                raise IntegrationError(
                    "Boundary generated-state Git exclusion block is malformed"
                )
            end = index

    if (start is None) != (end is None):
        raise IntegrationError(
            "Boundary generated-state Git exclusion block is malformed"
        )
    if start is None:
        return None
    return start, end
