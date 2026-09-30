#!/usr/bin/env python3
"""Project-local semantic entrypoint for an installed Boundary integration."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Sequence


_RUNTIME_RELATIVE = Path(".specify") / "boundary-runtime"
_ADAPTER_GATE_RELATIVE = (
    Path(".specify")
    / "extensions"
    / "boundary"
    / "scripts"
    / "adapter_gate.py"
)
_UV_CACHE_RELATIVE = Path(".boundary") / "cache" / "uv"


class ProjectEntrypointError(RuntimeError):
    """Raised when the installed project-local Boundary command cannot run."""


def parse_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="boundary",
        description="Run Boundary operations for this installed project.",
    )
    parser.add_argument(
        "command",
        choices=("inspect", "authorize", "verify", "status", "contracts"),
    )
    parser.add_argument(
        "arguments",
        nargs=argparse.REMAINDER,
        help="Arguments for the selected Boundary operation.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        root = _project_root()
        if args.command == "inspect":
            return _run_core(root, ("inspect", *args.arguments))
        if args.command == "contracts":
            if tuple(args.arguments) != ("check",):
                raise ProjectEntrypointError(
                    "contracts currently requires exactly the 'check' subcommand"
                )
            return _run_core(root, ("contracts", "check"))
        if args.command == "authorize":
            return _run_adapter(root, "authorize", tuple(args.arguments))
        if args.command == "verify":
            return _run_adapter(root, "verify", tuple(args.arguments))
        if args.command == "status":
            if args.arguments:
                raise ProjectEntrypointError(
                    "status does not accept additional arguments"
                )
            _print_status(root)
            return 0
    except (
        json.JSONDecodeError,
        OSError,
        ProjectEntrypointError,
    ) as exc:
        print(f"boundary: {exc}", file=sys.stderr)
        return 2

    raise AssertionError(f"unhandled command: {args.command}")


def _project_root() -> Path:
    entrypoint = Path(__file__).resolve()
    if (
        entrypoint.parent.name != "bin"
        or entrypoint.parent.parent.name != ".boundary"
    ):
        raise ProjectEntrypointError(
            "project-local Boundary entrypoint is not installed under "
            ".boundary/bin"
        )
    return entrypoint.parents[2]


def _run_core(
    root: Path,
    arguments: tuple[str, ...],
) -> int:
    runtime = root / _RUNTIME_RELATIVE
    if not runtime.is_dir():
        raise ProjectEntrypointError(
            "installed Boundary runtime is unavailable; reinstall Boundary"
        )

    command = [
        *_python_prefix(),
        "-m",
        "boundary",
        *arguments,
    ]
    result = subprocess.run(
        command,
        cwd=root,
        env=_runtime_environment(root),
        check=False,
    )
    return result.returncode


def _run_adapter(
    root: Path,
    stage: str,
    arguments: tuple[str, ...],
) -> int:
    gate = root / _ADAPTER_GATE_RELATIVE
    if not gate.is_file():
        raise ProjectEntrypointError(
            "installed change-system adapter is unavailable; reinstall Boundary"
        )

    command = [
        *_python_prefix(),
        str(gate),
        stage,
        "--root",
        str(root),
        *arguments,
    ]
    result = subprocess.run(
        command,
        cwd=root,
        env=_runtime_environment(root),
        check=False,
    )
    return result.returncode


def _python_prefix() -> list[str]:
    uv = shutil.which("uv")
    if uv is not None:
        return [uv, "run", "--no-project", "python"]
    return [sys.executable]


def _runtime_environment(root: Path) -> dict[str, str]:
    runtime = root / _RUNTIME_RELATIVE
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(runtime)
        if not existing
        else str(runtime) + os.pathsep + existing
    )
    env.setdefault(
        "UV_CACHE_DIR",
        str(root / _UV_CACHE_RELATIVE),
    )
    return env


def _print_status(root: Path) -> None:
    current = _current_operation_path(root)
    operation: object | None = None
    if current.is_file():
        operation = json.loads(current.read_text(encoding="utf-8"))

    print(
        json.dumps(
            {
                "schema": "boundary.status/v1",
                "operation": operation,
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
    )


def _current_operation_path(root: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", "boundary/current.json"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        detail = " ".join((result.stderr or result.stdout).split())
        raise ProjectEntrypointError(
            "could not locate Boundary operation evidence"
            + (f": {detail}" if detail else "")
        )

    path = Path(result.stdout.strip())
    if not path.is_absolute():
        path = root / path
    return path


if __name__ == "__main__":
    raise SystemExit(main())
