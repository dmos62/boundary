"""Boundary-owned agent skill installation and root ignore management."""

from pathlib import Path
import shutil
from typing import TextIO

from boundary.pre_change.model import PreChangeError

from boundary.operation.storage import require_managed_ignore, update_managed_ignore


def _skill_source(name: str) -> str:
    from importlib.resources import files
    candidate = files("boundary_assets").joinpath("skills", name, "SKILL.md")
    if candidate.is_file():
        return candidate.read_text(encoding="utf-8")
    return (Path(__file__).resolve().parents[3] / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


DESCRIPTIONS = {
    "scope": "Plan exact Boundary write scope and inspect effective contract context.",
    "implement": "Implement only within a successful Boundary pre-change operation.",
    "contracts": "Evolve persistent Boundary contracts as a separate operation.",
}


def _render_skill(name: str) -> str:
    payload = _skill_source(name)
    if not payload.endswith("\n"):
        payload += "\n"
    return (
        f"---\nname: boundary-{name}\n"
        f"description: {DESCRIPTIONS[name]}\n---\n\n{payload}"
    )


def _skill_targets(root: Path):
    for parent in (root / ".agents" / "skills", root / ".claude" / "skills"):
        for name in DESCRIPTIONS:
            yield name, parent / f"boundary-{name}" / "SKILL.md"


def _install_skills(root: Path) -> None:
    for name, target in _skill_targets(root):
        rendered = _render_skill(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or target.read_text(encoding="utf-8") != rendered:
            target.write_text(rendered, encoding="utf-8")


def _check_skills(root: Path) -> None:
    for name, target in _skill_targets(root):
        if not target.is_file() or target.read_text(encoding="utf-8") != _render_skill(name):
            raise PreChangeError(f"Boundary agent skill is missing or stale: {target}", code="INTEGRATION_STATE_INVALID")


def run_integration(root: Path, action: str, output: TextIO) -> int:
    from boundary.operation.storage import read_current_operation, worktree_root
    root = worktree_root(root)
    if action in {"install", "remove"}:
        current = read_current_operation(root)
        if current is not None and current.status == "open":
            raise PreChangeError("integration changes require the open operation to be closed", code="OPERATION_OPEN")
    if action == "install":
        _install_skills(root)
        update_managed_ignore(root, True)
    elif action == "check":
        _check_skills(root)
        require_managed_ignore(root)
    elif action == "remove":
        for parent in (root / ".agents" / "skills", root / ".claude" / "skills"):
            for name in ("scope", "implement", "contracts"):
                path = parent / f"boundary-{name}"
                if path.is_dir():
                    shutil.rmtree(path)
        update_managed_ignore(root, False)
    else:
        raise PreChangeError(f"unknown integration action: {action}")
    print(f"Boundary integration {action}: ok", file=output)
    return 0
