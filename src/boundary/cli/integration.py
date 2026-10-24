"""Worktree-state setup, independent of any agent runtime."""

from pathlib import Path
from typing import TextIO

from boundary.pre_change.model import PreChangeError
from boundary.operation.storage import (
    read_current_operation, require_managed_ignore, update_managed_ignore, worktree_root,
)


def run_setup(root: Path, action: str, output: TextIO) -> int:
    root = worktree_root(root)
    if action in {"install", "remove"}:
        current = read_current_operation(root)
        if current is not None and current.status == "open":
            raise PreChangeError("setup changes require the open operation to be closed", code="OPERATION_OPEN")
    if action == "install":
        update_managed_ignore(root, True)
    elif action == "check":
        require_managed_ignore(root)
    elif action == "remove":
        update_managed_ignore(root, False)
    else:
        raise PreChangeError(f"unknown setup action: {action}")
    print(f"Boundary setup {action}: ok", file=output)
    return 0
