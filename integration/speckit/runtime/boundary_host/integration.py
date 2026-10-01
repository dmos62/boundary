"""Installed CLI lifecycle for Boundary-owned project integration."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from .assets import asset_root
from .errors import IntegrationError
from .generated_state import (
    cleanup_legacy_generated_state,
    require_local_excludes,
    require_no_legacy_generated_state,
    update_local_excludes,
)
from .host_check import check_host, remove_host
from .host_install import install_host


def run_integration(
    root: Path,
    action: str,
    output: TextIO,
    errors: TextIO,
) -> int:
    """Run one installed Boundary integration lifecycle action."""

    try:
        if action == "install":
            _install(root)
            message = "Boundary project integration installed."
        elif action == "check":
            _check(root)
            message = "Boundary project integration is healthy."
        elif action == "remove":
            _remove(root)
            message = "Boundary project integration removed."
        else:
            raise IntegrationError(
                f"unsupported integration action: {action}"
            )
    except (IntegrationError, OSError, ValueError) as exc:
        print(f"boundary: error: {exc}", file=errors)
        return 2

    print(message, file=output)
    return 0


def _install(root: Path) -> None:
    assets = asset_root()
    install_host(root, assets)
    cleanup_legacy_generated_state(root)
    update_local_excludes(root, enabled=True)


def _check(root: Path) -> None:
    assets = asset_root()
    require_no_legacy_generated_state(root)
    check_host(root, assets)
    require_local_excludes(root)


def _remove(root: Path) -> None:
    remove_host(root)
    cleanup_legacy_generated_state(root)
    update_local_excludes(root, enabled=False)
