"""Atomic operation evidence beneath the current Git worktree root."""

import json
import os
from pathlib import Path
import subprocess
import tempfile

from boundary.pre_change.model import PreChangeError
from .codec import operation_record_from_document
from .git import git_metadata_directory
from .record import OperationRecord

OPERATION_EVIDENCE_UNAVAILABLE = "OPERATION_EVIDENCE_UNAVAILABLE"
STATE_ROOT = Path(".boundary-state")

BEGIN = "# BEGIN Boundary generated state"
END = "# END Boundary generated state"
RULES = (
    "/.boundary-state/",
    "/.agents/skills/boundary-scope/",
    "/.agents/skills/boundary-implement/",
    "/.agents/skills/boundary-contracts/",
    "/.claude/skills/boundary-scope/",
    "/.claude/skills/boundary-implement/",
    "/.claude/skills/boundary-contracts/",
)


def _span(lines: list[str]) -> tuple[int, int] | None:
    starts = [i for i, line in enumerate(lines) if line == BEGIN]
    ends = [i for i, line in enumerate(lines) if line == END]
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise PreChangeError("Boundary .gitignore markers are malformed", code="INTEGRATION_STATE_INVALID")
    return starts[0], ends[0]


def require_managed_ignore(root: Path) -> None:
    try:
        lines = (root / ".gitignore").read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise PreChangeError(f"Boundary .gitignore block is unavailable: {exc}", code="INTEGRATION_STATE_INVALID") from exc
    span = _span(lines)
    if span is None or tuple(lines[span[0]+1:span[1]]) != RULES:
        raise PreChangeError("Boundary .gitignore block is missing or stale; run boundary integration install", code="INTEGRATION_STATE_INVALID")


def update_managed_ignore(root: Path, enabled: bool) -> None:
    path = root / ".gitignore"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    span = _span(lines)
    if enabled and span is not None and tuple(lines[span[0]+1:span[1]]) == RULES:
        return
    if span is not None:
        lines = lines[:span[0]] + lines[span[1]+1:]
    while lines and not lines[-1]:
        lines.pop()
    if enabled:
        if lines:
            lines.append("")
        lines.extend((BEGIN, *RULES, END))
    rendered = "\n".join(lines) + ("\n" if lines else "")
    if not path.exists() or path.read_text(encoding="utf-8") != rendered:
        path.write_text(rendered, encoding="utf-8")




def worktree_root(repository_root: str | Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=repository_root, capture_output=True, text=True, check=False,
    )
    if result.returncode or not result.stdout.strip():
        raise PreChangeError("could not determine Git worktree root", code=OPERATION_EVIDENCE_UNAVAILABLE)
    return Path(result.stdout.strip()).resolve()


def state_directory(repository_root: str | Path) -> Path:
    root = worktree_root(repository_root)
    path = root / STATE_ROOT
    if path.is_symlink() or not path.resolve(strict=False).is_relative_to(root):
        raise PreChangeError("operation state path escapes the worktree", code=OPERATION_EVIDENCE_UNAVAILABLE)
    return path


def require_no_legacy_state(repository_root: str | Path) -> None:
    legacy = git_metadata_directory(repository_root) / "boundary"
    if legacy.exists() or legacy.is_symlink():
        raise PreChangeError(
            "legacy Git-metadata Boundary evidence exists; resolve it with the old version and clean it up before upgrading",
            code="LEGACY_OPERATION_EVIDENCE",
        )


def require_state_ready(repository_root: str | Path) -> None:
    """Require visible setup to ignore only this worktree's local evidence."""
    require_no_legacy_state(repository_root)
    root = worktree_root(repository_root)
    require_managed_ignore(root)
    result = subprocess.run(
        ["git", "ls-files", "--", ".boundary-state"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    if result.returncode or result.stdout.strip():
        raise PreChangeError(".boundary-state must be untracked", code=OPERATION_EVIDENCE_UNAVAILABLE)
    result = subprocess.run(
        ["git", "check-ignore", "-q", "--no-index", ".boundary-state/current.json"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise PreChangeError(".boundary-state is not ignored; run boundary integration install", code=OPERATION_EVIDENCE_UNAVAILABLE)


def check_operation_evidence_persistence(repository_root: str | Path) -> Path:
    directory = state_directory(repository_root)
    created = not directory.exists()
    try:
        directory.mkdir(exist_ok=True)
        fd, name = tempfile.mkstemp(dir=directory, prefix=".probe-")
        os.close(fd)
        Path(name).unlink()
        if created:
            directory.rmdir()
    except OSError as exc:
        raise PreChangeError(f"operation evidence cannot be persisted: {exc}", code=OPERATION_EVIDENCE_UNAVAILABLE) from exc
    return directory


def current_operation_path(repository_root: str | Path) -> Path:
    return state_directory(repository_root) / "current.json"


def operation_archive_path(repository_root: str | Path, operation_id: str) -> Path:
    if not operation_id or any(char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-" for char in operation_id):
        raise PreChangeError("operation id contains unsupported characters")
    path = state_directory(repository_root) / "predecessors"
    if path.is_symlink() or not path.resolve(strict=False).is_relative_to(worktree_root(repository_root)):
        raise PreChangeError("predecessor state path escapes the worktree", code=OPERATION_EVIDENCE_UNAVAILABLE)
    return path / f"{operation_id}.json"


def read_current_operation(repository_root: str | Path) -> OperationRecord | None:
    require_no_legacy_state(repository_root)
    path = current_operation_path(repository_root)
    if path.is_symlink():
        raise PreChangeError("current operation evidence is a symlink", code=OPERATION_EVIDENCE_UNAVAILABLE)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as exc:
        raise PreChangeError(f"could not read operation evidence: {exc}", code="OPERATION_EVIDENCE_INVALID") from exc
    return operation_record_from_document(value)


def write_current_operation(repository_root: str | Path, record: OperationRecord) -> Path:
    output = current_operation_path(repository_root)
    _atomic_replace(output, _render(record))
    return output


def archive_operation(repository_root: str | Path, record: OperationRecord) -> Path:
    if record.status != "verified":
        raise PreChangeError("only verified predecessors may be retained")
    output = operation_archive_path(repository_root, record.operation_id)
    rendered = _render(record)
    if output.is_symlink() or not output.resolve(strict=False).is_relative_to(worktree_root(repository_root)):
        raise PreChangeError("predecessor evidence path escapes the worktree", code=OPERATION_EVIDENCE_UNAVAILABLE)
    if output.exists():
        if output.read_text(encoding="utf-8") != rendered:
            raise PreChangeError("predecessor evidence differs")
        return output
    output.parent.mkdir(exist_ok=True)
    temporary = _temporary(output, rendered)
    try:
        os.link(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return output


def prune_predecessors(repository_root: str | Path, keep: set[str]) -> None:
    directory = state_directory(repository_root) / "predecessors"
    if not directory.exists():
        return
    if directory.is_symlink():
        raise PreChangeError("predecessor state path is a symlink", code=OPERATION_EVIDENCE_UNAVAILABLE)
    for path in directory.glob("*.json"):
        if path.stem not in keep:
            path.unlink()


def _render(record: OperationRecord) -> str:
    return json.dumps(record.to_document(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _temporary(output: Path, rendered: str) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, prefix=output.name + ".", suffix=".tmp", delete=False) as handle:
        handle.write(rendered)
        handle.flush()
        os.fsync(handle.fileno())
        return Path(handle.name)


def _atomic_replace(output: Path, rendered: str) -> None:
    if output.is_symlink():
        raise PreChangeError("operation evidence is a symlink", code=OPERATION_EVIDENCE_UNAVAILABLE)
    output.parent.mkdir(exist_ok=True)
    temporary = _temporary(output, rendered)
    try:
        os.replace(temporary, output)
    except OSError as exc:
        raise PreChangeError(f"could not store atomic operation evidence: {exc}", code=OPERATION_EVIDENCE_UNAVAILABLE) from exc
    finally:
        temporary.unlink(missing_ok=True)
