from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import consumer_lock
from consumer_lock import BoundaryLock, BoundaryLockError


class ConsumerSourceIntegrityTests(unittest.TestCase):
    def test_materialization_rejects_missing_consumer_state_helper(self) -> None:
        revision = "a" * 40
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            source_root = temp_root / f"boundary-{revision}"
            for relative in consumer_lock._REQUIRED_SOURCE_PATHS:
                if relative == "scripts/consumer_state.py":
                    continue
                path = source_root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture\n", encoding="utf-8")

            archive_base = temp_root / "fixture"
            archive = Path(
                shutil.make_archive(
                    str(archive_base),
                    "zip",
                    root_dir=temp_root,
                    base_dir=source_root.name,
                )
            )
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            lock = BoundaryLock(
                source_url=(
                    "https://github.com/example/boundary/archive/"
                    f"{revision}.zip"
                ),
                revision=revision,
                sha256=digest,
            )

            destination = temp_root / "materialized"

            def copy_archive(_url: str, output: Path) -> None:
                shutil.copyfile(archive, output)

            with mock.patch.object(
                consumer_lock,
                "_download",
                side_effect=copy_archive,
            ):
                with self.assertRaisesRegex(
                    BoundaryLockError,
                    r"scripts/consumer_state\.py",
                ):
                    consumer_lock.materialize_locked_source(lock, destination)


if __name__ == "__main__":
    unittest.main()
