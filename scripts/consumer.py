#!/usr/bin/env python3
"""Manage downstream Boundary state from one pinned source checkout."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
from typing import Sequence

from consumer_lock import (
    BoundaryLock,
    BoundaryLockError,
    load_lock,
    write_lock,
)
from consumer_source import (
    BoundarySourceCheckout,
    BoundarySourceError,
    load_source_checkout,
)
from consumer_state import (
    ConsumerStateError,
    require_local_excludes as _require_local_excludes,
    require_provenance as _require_provenance,
    update_local_excludes as _update_local_excludes,
    write_provenance as _write_provenance,
)

_DEFAULT_LOCK = "boundary.lock.json"


class ConsumerError(RuntimeError):
    """Raised when downstream Boundary lifecycle work cannot complete."""


def parse_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage downstream Boundary state from its pinned checkout."
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
    commands.add_parser("adopt")
    commands.add_parser("install")
    commands.add_parser("check")
    commands.add_parser("remove")
    commands.add_parser("reinstall")
    commands.add_parser("upgrade")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    lock_path = args.lock
    if not lock_path.is_absolute():
        lock_path = root / lock_path

    try:
        source = _source_checkout()
        if args.command == "adopt":
            _adopt(lock_path, source)
        elif args.command == "upgrade":
            _upgrade(root, lock_path, source)
        else:
            lock = load_lock(lock_path)
            _require_locked_source(lock, source)
            if args.command == "install":
                _install(root, lock, source)
            elif args.command == "check":
                _check(root, lock, source)
            elif args.command == "remove":
                _remove(root, source)
            elif args.command == "reinstall":
                _remove(root, source)
                _install(root, lock, source)
    except (
        BoundaryLockError,
        BoundarySourceError,
        ConsumerError,
        ConsumerStateError,
        OSError,
    ) as exc:
        print(f"boundary consumer: {exc}", file=sys.stderr)
        return 2
    return 0


def _source_checkout() -> BoundarySourceCheckout:
    return load_source_checkout(Path(__file__))


def _adopt(
    lock_path: Path,
    source: BoundarySourceCheckout,
) -> None:
    if lock_path.exists():
        raise ConsumerError(
            f"Boundary lock already exists: {lock_path}"
        )
    write_lock(lock_path, BoundaryLock(revision=source.revision))


def _require_locked_source(
    lock: BoundaryLock,
    source: BoundarySourceCheckout,
) -> None:
    if source.revision != lock.revision:
        raise ConsumerError(
            "Boundary source checkout revision does not match "
            f"boundary.lock.json: expected {lock.revision}, "
            f"received {source.revision}"
        )


def _install(
    root: Path,
    lock: BoundaryLock,
    source: BoundarySourceCheckout,
) -> None:
    _with_source(root, source, "install")
    _write_provenance(root, lock)
    _update_local_excludes(root, enabled=True)


def _check(
    root: Path,
    lock: BoundaryLock,
    source: BoundarySourceCheckout,
) -> None:
    _require_provenance(root, lock)
    _with_source(root, source, "check")
    _require_local_excludes(root)


def _remove(root: Path, source: BoundarySourceCheckout) -> None:
    _with_source(root, source, "remove")
    _update_local_excludes(root, enabled=False)


def _upgrade(
    root: Path,
    lock_path: Path,
    source: BoundarySourceCheckout,
) -> None:
    previous = load_lock(lock_path)
    if source.revision == previous.revision:
        raise ConsumerError(
            "upgrade requires a Boundary source checkout at a different revision"
        )

    replacement = BoundaryLock(revision=source.revision)
    try:
        _install(root, replacement, source)
    except Exception as exc:
        raise ConsumerError(
            f"candidate Boundary installation failed: {exc}. "
            "boundary.lock.json remains "
            f"at {previous.revision}. Recovery requires a Boundary checkout at "
            "that still-locked revision"
        ) from exc
    write_lock(lock_path, replacement)


def _with_source(
    root: Path,
    source: BoundarySourceCheckout,
    action: str,
) -> None:
    command = ["bash", str(source.root / "scripts" / "install.sh")]
    if action == "install":
        command.extend(["--source", str(source.root)])
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
            f"Boundary {action} failed with exit status {result.returncode}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
