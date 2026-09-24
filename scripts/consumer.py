#!/usr/bin/env python3
"""Manage downstream Boundary state from one committed immutable lock."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Sequence

from consumer_lock import (
    BoundaryLock,
    BoundaryLockError,
    load_lock,
    materialize_locked_source,
    write_lock,
)
from consumer_state import (
    GENERATED_EXCLUDES as _GENERATED_EXCLUDES,
    ConsumerStateError,
    require_local_excludes as _require_local_excludes,
    require_provenance as _require_provenance,
    update_local_excludes as _update_local_excludes,
    write_provenance as _write_provenance,
)

_DEFAULT_LOCK = "boundary.lock.json"


class ConsumerError(RuntimeError):
    """Raised when downstream reconstruction cannot complete safely."""


def parse_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reconstruct downstream Boundary state from its lock."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Downstream repository root.",
    )
    parser.add_argument(
        "--lock",
        type=Path,
        default=Path(_DEFAULT_LOCK),
        help="Boundary lock path, relative to the downstream root by default.",
    )

    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("install")
    commands.add_parser("check")
    commands.add_parser("remove")
    commands.add_parser("reinstall")

    upgrade = commands.add_parser("upgrade")
    upgrade.add_argument("--source", required=True)
    upgrade.add_argument("--revision", required=True)
    upgrade.add_argument("--sha256", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    lock_path = args.lock
    if not lock_path.is_absolute():
        lock_path = root / lock_path

    try:
        if args.command == "upgrade":
            replacement = BoundaryLock(
                source_url=args.source,
                revision=args.revision,
                sha256=args.sha256,
            )
            _upgrade(root, lock_path, replacement)
        else:
            lock = load_lock(lock_path)
            if args.command == "install":
                _install(root, lock)
            elif args.command == "check":
                _check(root, lock)
            elif args.command == "remove":
                _remove(root, lock)
            elif args.command == "reinstall":
                _remove(root, lock)
                _install(root, lock)
    except (
        BoundaryLockError,
        ConsumerError,
        ConsumerStateError,
        OSError,
    ) as exc:
        print(f"boundary consumer: {exc}", file=sys.stderr)
        return 2
    return 0


def _install(root: Path, lock: BoundaryLock) -> None:
    _with_source(root, lock, "install")
    _write_provenance(root, lock)
    _update_local_excludes(root, enabled=True)


def _check(root: Path, lock: BoundaryLock) -> None:
    _require_provenance(root, lock)
    _with_source(root, lock, "check")
    _require_local_excludes(root)


def _remove(root: Path, lock: BoundaryLock) -> None:
    _with_source(root, lock, "remove")
    _update_local_excludes(root, enabled=False)


def _upgrade(
    root: Path,
    lock_path: Path,
    replacement: BoundaryLock,
) -> None:
    previous = load_lock(lock_path)
    try:
        _install(root, replacement)
        write_lock(lock_path, replacement)
    except Exception as exc:
        try:
            _install(root, previous)
        except Exception as rollback_exc:
            raise ConsumerError(
                "upgrade failed and the previous locked installation could "
                f"not be restored: {rollback_exc}"
            ) from exc
        raise


def _with_source(
    root: Path,
    lock: BoundaryLock,
    action: str,
) -> None:
    with tempfile.TemporaryDirectory(prefix="boundary-consumer-") as temp:
        source_root = materialize_locked_source(lock, temp)
        command = ["bash", str(source_root / "scripts" / "install.sh")]
        if action == "install":
            command.extend(["--source", str(source_root)])
        elif action == "check":
            command.append("--check")
        elif action == "remove":
            command.append("--remove")
        else:
            raise ConsumerError(f"unsupported consumer action: {action}")

        result = subprocess.run(
            command,
            cwd=root,
            check=False,
        )
        if result.returncode != 0:
            raise ConsumerError(
                f"locked Boundary {action} failed with exit "
                f"status {result.returncode}"
            )


if __name__ == "__main__":
    raise SystemExit(main())
