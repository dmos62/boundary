"""Optional, runtime-neutral delivery of Boundary's canonical skills."""

from importlib.resources import files
import os
from pathlib import Path
import tempfile
from typing import TextIO

from boundary.operation.storage import read_current_operation, worktree_root
from boundary.pre_change.model import PreChangeError
from boundary.repository import normalize_repo_path


DESCRIPTIONS = {
    "scope": "Plan exact Boundary write scope and inspect effective contract context.",
    "implement": "Implement only within a successful Boundary pre-change operation.",
    "contracts": "Evolve persistent Boundary contracts as a separate operation.",
}


def _directory(root: Path, value: str) -> Path:
    relative = normalize_repo_path(value)
    if relative.split("/", 1)[0] in {".git", ".boundary-state"}:
        raise PreChangeError("skill directory overlaps Boundary or Git state")
    if any(ord(char) < 32 or ord(char) == 127 for char in relative):
        raise PreChangeError("skill directory contains control characters")
    directory = root / relative
    for part in (directory, *directory.parents):
        if part == root:
            break
        if part.is_symlink():
            raise PreChangeError(f"skill directory contains a symlink: {part}")
        if part.exists() and not part.is_dir():
            raise PreChangeError(f"skill directory component is not a directory: {part}")
    if not directory.resolve(strict=False).is_relative_to(root):
        raise PreChangeError("skill directory escapes the worktree")
    return directory


def _targets(directory: Path):
    for name in DESCRIPTIONS:
        yield name, directory / f"boundary-{name}" / "SKILL.md"


def _render(name: str) -> bytes:
    asset = files("boundary_assets").joinpath("skills", name, "SKILL.md")
    if asset.is_file():
        body = asset.read_bytes()
    else:
        body = (Path(__file__).resolve().parents[3] / "skills" / name / "SKILL.md").read_bytes()
    header = f"---\nname: boundary-{name}\ndescription: {DESCRIPTIONS[name]}\n---\n\n".encode()
    return header + body.rstrip(b"\n") + b"\n"


def _owned(path: Path, name: str) -> bool:
    return path.read_bytes().startswith(f"---\nname: boundary-{name}\n".encode())


def run_skills(root: Path, action: str, directory: str, output: TextIO) -> int:
    root = worktree_root(root)
    destination = _directory(root, directory)
    if action in {"install", "remove"}:
        current = read_current_operation(root)
        if current is not None and current.status == "open":
            raise PreChangeError("skill changes require the open operation to be closed", code="OPERATION_OPEN")
    targets = tuple(_targets(destination))
    for name, path in targets:
        if path.parent.is_symlink() or path.is_symlink():
            raise PreChangeError(f"skill target is a symlink: {path}")
        if path.parent.exists() and not path.parent.is_dir():
            raise PreChangeError(f"skill directory is not a directory: {path.parent}")
        if path.exists() and (not path.is_file() or not _owned(path, name)):
            raise PreChangeError(f"skill target is not Boundary-owned: {path}")
    if action == "install":
        payloads = {name: _render(name) for name, _ in targets}
        for name, path in targets:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and path.read_bytes() == payloads[name]:
                continue
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".SKILL-", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(payloads[name])
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
    elif action == "check":
        for name, path in targets:
            if not path.is_file() or path.read_bytes() != _render(name):
                raise PreChangeError(f"Boundary skill is missing or stale: {path}", code="INTEGRATION_STATE_INVALID")
    elif action == "remove":
        for _, path in targets:
            if path.exists():
                path.unlink()
                if not any(path.parent.iterdir()):
                    path.parent.rmdir()
    else:
        raise PreChangeError(f"unknown skills action: {action}")
    print(f"Boundary skills {action}: ok", file=output)
    return 0
