"""Spec Kit repository and active-feature discovery."""

from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

from spec_kit_errors import SpecKitAdapterError


def resolve_repository_root(value: str | Path | None = None) -> Path:
    """Resolve the repository root explicitly or through Git."""

    if value is not None:
        return Path(value).resolve()

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise SpecKitAdapterError(
            "required command not found: git",
            code="MISSING_EXTERNAL_PREREQUISITE",
        ) from exc
    except OSError as exc:
        raise SpecKitAdapterError(
            f"Git could not be executed: {exc}",
            code="MISSING_EXTERNAL_PREREQUISITE",
        ) from exc

    if result.returncode != 0 or not result.stdout.strip():
        detail = " ".join((result.stderr or result.stdout).split())
        raise SpecKitAdapterError(
            "could not determine repository root"
            + (f": {detail}" if detail else "")
        )
    return Path(result.stdout.strip()).resolve()


def active_feature(root: Path) -> tuple[Path, str]:
    """Resolve the active Spec Kit feature directory and repository path."""

    configured = os.environ.get("SPECIFY_FEATURE_DIRECTORY")
    if configured:
        return _feature_path(root, configured)

    command = _prerequisite_command(root)
    try:
        result = subprocess.run(
            command,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise SpecKitAdapterError(
            f"required command not found: {command[0]}",
            code="MISSING_EXTERNAL_PREREQUISITE",
        ) from exc
    except OSError as exc:
        raise SpecKitAdapterError(
            f"required command could not be executed: {command[0]}: {exc}",
            code="MISSING_EXTERNAL_PREREQUISITE",
        ) from exc

    if result.returncode != 0:
        detail = " ".join((result.stderr or result.stdout).split())
        raise SpecKitAdapterError(
            "Spec Kit could not resolve the active feature"
            + (f": {detail}" if detail else "")
        )
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SpecKitAdapterError(
            "Spec Kit prerequisite discovery returned invalid JSON"
        ) from exc

    feature = value.get("FEATURE_DIR")
    if not isinstance(feature, str) or not feature:
        raise SpecKitAdapterError(
            "Spec Kit prerequisite discovery did not return FEATURE_DIR"
        )
    return _feature_path(root, feature)


def _prerequisite_command(root: Path) -> list[str]:
    mode = _configured_script_mode(root)
    scripts = root / ".specify" / "scripts"

    if mode == "sh":
        script = scripts / "bash" / "check-prerequisites.sh"
        command = ["bash", str(script), "--json", "--paths-only"]
    elif mode == "ps":
        script = scripts / "powershell" / "check-prerequisites.ps1"
        command = ["pwsh", str(script), "-Json", "-PathsOnly"]
    elif mode == "py":
        script = scripts / "python" / "check_prerequisites.py"
        command = [
            sys.executable,
            str(script),
            "--json",
            "--paths-only",
        ]
    else:
        raise SpecKitAdapterError(
            f"unsupported configured Spec Kit script mode: {mode}"
        )

    if not script.is_file():
        raise SpecKitAdapterError(
            f"Spec Kit prerequisite discovery is unavailable for {mode} mode",
            code="MISSING_EXTERNAL_PREREQUISITE",
        )
    return command


def _configured_script_mode(root: Path) -> str:
    options_path = root / ".specify" / "init-options.json"
    try:
        options = json.loads(options_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SpecKitAdapterError(
            f"Spec Kit init options are unavailable: {options_path}: {exc}",
            code="MISSING_EXTERNAL_PREREQUISITE",
        ) from exc
    except json.JSONDecodeError as exc:
        raise SpecKitAdapterError(
            f"Spec Kit init options contain invalid JSON: {options_path}"
        ) from exc

    mode = options.get("script") if isinstance(options, dict) else None
    if not isinstance(mode, str) or not mode:
        raise SpecKitAdapterError(
            "Spec Kit init options do not select a script mode"
        )
    return mode


def _feature_path(root: Path, configured: str) -> tuple[Path, str]:
    normalized = configured.replace("\\", "/")
    raw = PurePosixPath(normalized)
    candidate = Path(*raw.parts)
    if raw.is_absolute():
        candidate = Path(normalized)
    else:
        candidate = root / candidate

    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise SpecKitAdapterError(
            "active Spec Kit feature is outside the repository root"
        ) from exc
    if not resolved.is_dir():
        raise SpecKitAdapterError(
            f"active Spec Kit feature does not exist: {relative}"
        )
    return resolved, relative
