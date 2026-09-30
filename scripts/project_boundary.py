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
_ADAPTER_GATE_RELATIVE = Path(".specify") / "extensions" / "boundary" / "scripts" / "adapter_gate.py"
_UV_CACHE_RELATIVE = Path(".boundary") / "cache" / "uv"


class ProjectEntrypointError(RuntimeError):
    """Raised when the installed project-local Boundary command cannot run."""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
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
    except (json.JSONDecodeError, OSError, ProjectEntrypointError) as exc:
        print(f"boundary: {exc}", file=sys.stderr)
        return 2
    raise AssertionError(f"unhandled command: {args.command}")


def _project_root() -> Path:
    entrypoint = Path(__file__).resolve()
    if entrypoint.parent.name != "bin" or entrypoint.parent.parent.name != ".boundary":
        raise ProjectEntrypointError(
            "project-local Boundary entrypoint is not installed under .boundary/bin"
        )
    return entrypoint.parents[2]


def _run_core(root: Path, arguments: tuple[str, ...]) -> int:
    runtime = root / _RUNTIME_RELATIVE
    if not runtime.is_dir():
        raise ProjectEntrypointError(
            "installed Boundary runtime is unavailable; reinstall Boundary"
        )
    result = subprocess.run(
        [*_python_prefix(), "-m", "boundary", *arguments],
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
    result = subprocess.run(
        [
            *_python_prefix(),
            str(gate),
            stage,
            "--root",
            str(root),
            *arguments,
        ],
        cwd=root,
        env=_runtime_environment(root),
        check=False,
    )
    return result.returncode


def _python_prefix() -> list[str]:
    uv = shutil.which("uv")
    return [uv, "run", "--no-project", "python"] if uv else [sys.executable]


def _runtime_environment(root: Path) -> dict[str, str]:
    runtime = root / _RUNTIME_RELATIVE
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(runtime) if not existing else str(runtime) + os.pathsep + existing
    )
    env.setdefault("UV_CACHE_DIR", str(root / _UV_CACHE_RELATIVE))
    return env


def _print_status(root: Path) -> None:
    current = _current_operation_path(root)
    record: dict[str, object] | None = None
    if current.is_file():
        value = json.loads(current.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ProjectEntrypointError(
                "Boundary operation evidence must be a JSON object"
            )
        record = value
    head = _git_head(root)
    baseline_head = _baseline_head(record)
    print(
        json.dumps(
            {
                "schema": "boundary.status/v2",
                "operation": _operation_capsule(record),
                "freshness": {
                    "baselineHead": baseline_head,
                    "currentHead": head,
                    "headMatchesBaseline": (
                        None if baseline_head is None else baseline_head == head
                    ),
                },
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
    )


def _operation_capsule(record: dict[str, object] | None) -> dict[str, object] | None:
    if record is None:
        return None
    result: dict[str, object] = {
        "operationId": record.get("operationId"),
        "status": record.get("status"),
        "kind": record.get("kind"),
        "changeId": _first(record, "changeId", "featureId", "feature", "change"),
        "selectedTaskIds": record.get("selectedTaskIds", []),
        "authorizedTargets": (
            _first(record, "authorizedTargets", "resolvedTargets", "targets") or []
        ),
    }
    contexts = _first(
        record,
        "targetContexts",
        "resolvedTargetContexts",
        "effectiveContexts",
        "contexts",
    )
    if contexts is not None:
        result["targetContexts"] = contexts
    return result


def _first(record: dict[str, object], *names: str) -> object | None:
    for name in names:
        if name in record:
            return record[name]
    return None


def _baseline_head(record: dict[str, object] | None) -> str | None:
    if record is None:
        return None
    for container_name in ("gitBaseline", "baseline", "git"):
        container = record.get(container_name)
        if isinstance(container, dict):
            for name in ("head", "headCommit", "commit", "revision"):
                value = container.get(name)
                if isinstance(value, str) and len(value) == 40:
                    return value.lower()
    for name in ("baselineHead", "baselineCommit", "head", "headCommit"):
        value = record.get(name)
        if isinstance(value, str) and len(value) == 40:
            return value.lower()
    return None


def _git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD^{commit}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise ProjectEntrypointError("could not determine current Git HEAD")
    return result.stdout.strip().lower()


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
    return path if path.is_absolute() else root / path


if __name__ == "__main__":
    raise SystemExit(main())
