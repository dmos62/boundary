#!/usr/bin/env python3
"""Run native Boundary transitions for the concrete Spec Kit adapter."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
SPECIFY_ROOT = SCRIPT_DIR.parents[2]
RUNTIME_ROOT = SPECIFY_ROOT / "boundary-runtime"
if RUNTIME_ROOT.is_dir() and str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from boundary.authorization import AuthorizationError  # noqa: E402
from boundary.verification import VerificationError  # noqa: E402
from spec_kit_adapter import (  # noqa: E402
    SpecKitAdapterError,
    active_feature,
    authorize_feature,
    resolve_repository_root,
    verify_feature,
)

_TASK_SELECTION_ENV = "BOUNDARY_TASK_IDS"


def parse_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Boundary transitions for the Spec Kit adapter."
    )
    parser.add_argument(
        "stage",
        choices=("authorize", "verify"),
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
            "to a JSON array"
        )
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpecKitAdapterError(
            "BOUNDARY_TASK_IDS must contain a JSON array of task ids"
        ) from exc
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise SpecKitAdapterError(
            "BOUNDARY_TASK_IDS must contain a non-empty JSON array "
            "of non-empty task ids"
        )
    return tuple(value)


def run_stage(
    root: Path,
    stage: str,
    selected_task_ids: tuple[str, ...] = (),
) -> dict[str, object]:
    """Run one adapter lifecycle transition and return stable JSON output."""

    feature_dir, feature_path = active_feature(root)
    if stage == "authorize":
        record = authorize_feature(
            root,
            feature_dir,
            selected_task_ids,
        )
    else:
        record = verify_feature(root, feature_dir)

    return {
        "adapter": "speckit",
        "feature": feature_path,
        "operation": record.to_document(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        selected_task_ids = resolve_task_selection(
            args.stage,
            args.task_ids,
        )
        root = resolve_repository_root(args.root)
        value = run_stage(
            root,
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
        print(f"boundary Spec Kit adapter: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
