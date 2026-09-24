"""Tests for revision-only downstream Boundary source locks."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from consumer_lock import (  # noqa: E402
    BoundaryLock,
    BoundaryLockError,
    load_lock,
    write_lock,
)


class BoundaryLockTests(unittest.TestCase):
    def test_round_trips_exact_revision_only_source_identity(self) -> None:
        lock = BoundaryLock(revision="a" * 40)

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "boundary.lock.json"
            write_lock(path, lock)
            loaded = load_lock(path)
            document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(loaded, lock)
        self.assertEqual(
            {
                "schema": "boundary.lock/v2",
                "source": {"revision": "a" * 40},
            },
            document,
        )

    def test_normalizes_uppercase_revision(self) -> None:
        lock = BoundaryLock(revision="A" * 40)
        self.assertEqual("a" * 40, lock.revision)

    def test_rejects_malformed_revision(self) -> None:
        with self.assertRaisesRegex(
            BoundaryLockError,
            "40-character Git commit id",
        ):
            BoundaryLock(revision="main")

    def test_rejects_archive_fields(self) -> None:
        document = {
            "schema": "boundary.lock/v2",
            "source": {
                "revision": "a" * 40,
                "url": "https://example.invalid/source.tar.gz",
                "sha256": "b" * 64,
            },
        }

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "boundary.lock.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(
                BoundaryLockError,
                "contain only revision",
            ):
                load_lock(path)

    def test_rejects_v1_schema(self) -> None:
        document = {
            "schema": "boundary.lock/v1",
            "source": {"revision": "a" * 40},
        }

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "boundary.lock.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(
                BoundaryLockError,
                "boundary.lock/v2",
            ):
                load_lock(path)


if __name__ == "__main__":
    unittest.main()
