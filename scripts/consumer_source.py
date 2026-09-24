"""Boundary source-checkout discovery and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

_REVISION_RE = re.compile(r"^[0-9a-f]{40}$")


class BoundarySourceError(RuntimeError):
    """Raised when the invoking Boundary source checkout is unusable."""


@dataclass(frozen=True, slots=True)
class BoundarySourceCheckout:
    """Validated local Boundary source used for one consumer invocation."""

    root: Path
    revision: str


def load_source_checkout(
    consumer_path: str | Path,
) -> BoundarySourceCheckout:
    """Resolve and validate the checkout containing the invoked consumer."""

    root = Path(consumer_path).resolve().parent.parent
    top_level = _git_output(
        root,
        "rev-parse",
        "--show-toplevel",
        failure="Boundary source is not a Git worktree",
    )
    discovered = Path(top_level).resolve()
    if discovered != root:
        raise BoundarySourceError(
            "Boundary consumer is not located at the source checkout root"
        )

    revision = _git_output(
        root,
        "rev-parse",
        "--verify",
        "HEAD^{commit}",
        failure="Boundary source HEAD is not an exact Git commit",
    ).lower()
    if _REVISION_RE.fullmatch(revision) is None:
        raise BoundarySourceError(
            "Boundary source HEAD must be a 40-character Git commit id"
        )

    status = _run_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0:
        raise BoundarySourceError(
            _failure_message(
                "Boundary source cleanliness could not be determined",
                status,
            )
        )
    if status.stdout.strip():
        raise BoundarySourceError("Boundary source checkout must be clean")

    return BoundarySourceCheckout(root=root, revision=revision)


def _git_output(root: Path, *args: str, failure: str) -> str:
    result = _run_git(root, *args)
    if result.returncode != 0 or not result.stdout.strip():
        raise BoundarySourceError(_failure_message(failure, result))
    return result.stdout.strip()


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def _failure_message(
    summary: str,
    result: subprocess.CompletedProcess[str],
) -> str:
    detail = " ".join((result.stderr or result.stdout).split())
    return summary + (f": {detail}" if detail else "")
