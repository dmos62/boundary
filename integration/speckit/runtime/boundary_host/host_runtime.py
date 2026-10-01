"""Shared host-runtime primitives for the concrete Spec Kit integration."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Sequence

from .errors import IntegrationError

SPECKIT_VERSION = "1.0.10"
ACTIVE_INTEGRATION = "codex"
EXTENSION_ID = "boundary"
PRESET_ID = "boundary"
WORKFLOW_ID = "speckit"
WORKFLOW_OVERLAY_ID = "boundary"
WORKFLOW_OVERLAY_PRIORITY = "10"
SCRIPT_OVERRIDE_ENV = "BOUNDARY_SPECKIT_SCRIPT"


def require_base_prerequisites(root: Path) -> None:
    """Require the concrete host tools used by Boundary integration."""

    require_command("git")
    require_command("specify")
    require_command("codex")
    result = run(root, ["git", "rev-parse", "--is-inside-work-tree"])
    if result.stdout.strip() != "true":
        raise IntegrationError("current directory is not a Git working tree")

    version = run(root, ["specify", "--version"])
    pattern = rf"(^|[^0-9]){re.escape(SPECKIT_VERSION)}([^0-9]|$)"
    if re.search(pattern, version.stdout + version.stderr) is None:
        raise IntegrationError(f"Spec Kit {SPECKIT_VERSION} is required")


def active_integration(root: Path) -> str | None:
    """Return the active Spec Kit integration, when configured."""

    path = root / ".specify" / "integration.json"
    if not path.is_file():
        return None
    value = read_json_object(path, "Spec Kit integration")
    active = value.get("default_integration") or value.get("integration")
    return active if isinstance(active, str) and active else None


def selected_script_mode(root: Path) -> str:
    """Return the authoritative Spec Kit script mode."""

    path = root / ".specify" / "init-options.json"
    value = read_json_object(path, "Spec Kit init options")
    mode = value.get("script")
    if mode not in {"sh", "ps", "py"}:
        raise IntegrationError(
            f"unsupported Spec Kit script mode in {path}: {mode!r}"
        )
    return str(mode)


def script_override() -> str | None:
    """Read one deliberate Spec Kit script-mode transition request."""

    value = os.environ.get(SCRIPT_OVERRIDE_ENV)
    if value is None or not value:
        return None
    if value not in {"sh", "ps", "py"}:
        raise IntegrationError(
            f"{SCRIPT_OVERRIDE_ENV} must be one of: sh, ps, py"
        )
    return value


def require_script_runtime(mode: str) -> None:
    """Require the host runtime selected by Spec Kit."""

    if mode == "sh":
        require_command("bash")
    elif mode == "ps":
        require_command("pwsh")


def read_json_object(path: Path, label: str) -> dict[str, object]:
    """Read one required JSON object with a stable integration error."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrationError(
            f"{label} is unavailable or invalid: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise IntegrationError(f"{label} must be a JSON object: {path}")
    return value


def require_command(name: str) -> None:
    """Require one host executable."""

    if shutil.which(name) is None:
        raise IntegrationError(f"required command not found: {name}")


def run(
    root: Path,
    args: Sequence[str],
    *,
    allow_failure: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run one host lifecycle command and fail with compact diagnostics."""

    try:
        result = subprocess.run(
            list(args),
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise IntegrationError(
            f"required command not found: {args[0]}"
        ) from exc
    except OSError as exc:
        raise IntegrationError(
            f"required command could not be executed: {args[0]}: {exc}"
        ) from exc

    if result.returncode != 0 and not allow_failure:
        detail = " ".join((result.stderr or result.stdout).split())
        command = " ".join(args)
        raise IntegrationError(
            f"command failed ({result.returncode}): {command}"
            + (f": {detail}" if detail else "")
        )
    return result
