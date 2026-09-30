#!/usr/bin/env python3
"""Run native Boundary actions for the concrete Spec Kit adapter."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Sequence, TextIO

SCRIPT_DIR = Path(__file__).resolve().parent
SPECIFY_ROOT = SCRIPT_DIR.parents[2]
RUNTIME_ROOT = SPECIFY_ROOT / "boundary-runtime"
if RUNTIME_ROOT.is_dir() and str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from boundary.authorization import (  # noqa: E402
    AuthorizationError,
    read_authorization_handoff,
    read_current_operation,
)
from boundary.verification import VerificationError  # noqa: E402
from lifecycle_outcome import outcome_for_error  # noqa: E402
from spec_kit_adapter import (  # noqa: E402
    SpecKitAdapterError,
    active_feature,
    authorize_feature,
    preflight_declared_scope,
    resolve_repository_root,
    verify_feature,
)

_TASK_SELECTION_ENV = "BOUNDARY_TASK_IDS"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Boundary actions for the Spec Kit adapter."
    )
    parser.add_argument(
        "stage",
        choices=("preflight", "authorize", "verify", "status"),
    )
    parser.add_argument(
        "--root",
        help="Repository root; defaults to Git discovery.",
    )
    parser.add_argument(
        "--task",
        action="append",
        dest="task_ids",
        default=[],
        help="Select one implementation task; repeat for multi-task units.",
    )
    return parser.parse_args(argv)


def resolve_task_selection(
    stage: str,
    task_ids: Sequence[str],
) -> tuple[str, ...]:
    """Resolve explicit implementation-unit input without an all-task fallback."""

    if stage != "authorize":
        return ()
    supplied = tuple(task_ids)
    if supplied:
        return supplied

    raw = os.environ.get(_TASK_SELECTION_ENV)
    if raw is None or not raw.strip():
        raise SpecKitAdapterError(
            "implementation authorization requires explicit task ids; "
            "pass --task for each selected task or set BOUNDARY_TASK_IDS "
            "to a JSON array",
            code="INVALID_TASK_SELECTION",
        )
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpecKitAdapterError(
            "BOUNDARY_TASK_IDS must contain a JSON array of task ids",
            code="INVALID_TASK_SELECTION",
        ) from exc
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise SpecKitAdapterError(
            "BOUNDARY_TASK_IDS must contain a non-empty JSON array "
            "of non-empty task ids",
            code="INVALID_TASK_SELECTION",
        )
    return tuple(value)


def run_stage(
    root: Path,
    stage: str,
    selected_task_ids: tuple[str, ...] = (),
) -> dict[str, object]:
    """Run one adapter action and return stable JSON output."""

    feature_dir, feature_path = active_feature(root)
    return _run_resolved_stage(
        root,
        feature_dir,
        feature_path,
        stage,
        selected_task_ids,
    )


def _run_resolved_stage(
    root: Path,
    feature_dir: Path,
    feature_path: str,
    stage: str,
    selected_task_ids: tuple[str, ...],
) -> dict[str, object]:
    if stage == "preflight":
        contexts = preflight_declared_scope(root, feature_dir)
        return {
            "adapter": "speckit",
            "feature": feature_path,
            "preflight": {
                "status": "ready",
                "targets": [
                    {
                        "path": context.target_path,
                        "owner": context.owner_id,
                        "applicableContracts": list(
                            context.applicable_contract_ids
                        ),
                    }
                    for context in contexts
                ],
            },
        }

    if stage == "status":
        handoff = read_authorization_handoff(root)
        return {
            "adapter": "speckit",
            "feature": feature_path,
            "authorizationState": (
                None if handoff is None else handoff.to_document()
            ),
            "matchesActiveFeature": (
                None
                if handoff is None
                else handoff.change_id == feature_dir.name
            ),
        }

    if stage == "authorize":
        record = authorize_feature(root, feature_dir, selected_task_ids)
    else:
        record = verify_feature(root, feature_dir)
    return {
        "adapter": "speckit",
        "feature": feature_path,
        "operation": record.to_document(),
    }


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    args = parse_args(argv)
    output = stdout if stdout is not None else sys.stdout
    errors = stderr if stderr is not None else sys.stderr
    root: Path | None = None
    change_id: str | None = None

    try:
        selected_task_ids = resolve_task_selection(args.stage, args.task_ids)
        root = resolve_repository_root(args.root)
        feature_dir, feature_path = active_feature(root)
        change_id = feature_dir.name
        value = _run_resolved_stage(
            root,
            feature_dir,
            feature_path,
            args.stage,
            selected_task_ids,
        )
    except (
        AuthorizationError,
        VerificationError,
        SpecKitAdapterError,
        OSError,
        ValueError,
    ) as exc:
        operation_id = (
            _current_operation_id(root)
            if root is not None and args.stage != "preflight"
            else None
        )
        outcome = outcome_for_error(
            args.stage,
            exc,
            change_id=change_id,
            operation_id=operation_id,
        )
        print(
            json.dumps(
                outcome.to_document(),
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=output,
        )
        print(f"boundary Spec Kit adapter: {exc}", file=errors)
        return 2

    print(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        file=output,
    )
    return 0


def _current_operation_id(root: Path) -> str | None:
    try:
        current = read_current_operation(root)
    except (AuthorizationError, OSError, ValueError):
        return None
    return None if current is None else current.operation_id


if __name__ == "__main__":
    raise SystemExit(main())
