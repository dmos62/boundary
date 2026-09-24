"""Consumer lifecycle coverage using operator-supplied source checkouts."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TESTS = Path(__file__).resolve().parent
for path in (SCRIPTS, TESTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from consumer_lock import load_lock  # noqa: E402
from consumer_test_support import (  # noqa: E402
    assert_no_boundary_generated_status,
    clone_fixture,
    initialize_fixture,
    make_source_checkout,
    run_consumer,
    run_git,
    status_paths,
)


@unittest.skipUnless(shutil.which("git"), "Git is required")
class ConsumerCheckoutLifecycleTests(unittest.TestCase):
    def test_first_adoption_records_source_without_installing_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            expected, source = make_source_checkout(
                temp / "boundary",
                "adopted",
            )
            consumer = temp / "consumer"
            self._initialize_unadopted_project(consumer)

            self.assertEqual(0, run_consumer(consumer, source, "adopt"))

            self.assertEqual(
                expected,
                load_lock(consumer / "boundary.lock.json"),
            )
            self.assertEqual(
                ("boundary.lock.json",),
                status_paths(consumer),
            )
            self.assertFalse((consumer / ".agents").exists())
            self.assertFalse((consumer / ".specify").exists())

    def test_adoption_rejects_existing_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            locked, source = make_source_checkout(
                temp / "boundary",
                "locked",
            )
            consumer = temp / "consumer"
            consumer.mkdir()
            initialize_fixture(consumer, locked)

            self.assertEqual(2, run_consumer(consumer, source, "adopt"))

            self.assertEqual(
                locked,
                load_lock(consumer / "boundary.lock.json"),
            )
            self.assertFalse(
                (consumer / ".specify" / "boundary-runtime").exists()
            )

    def test_adoption_rejects_dirty_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            _, source = make_source_checkout(temp / "boundary", "dirty")
            consumer = temp / "consumer"
            self._initialize_unadopted_project(consumer)
            (source / "dirty.txt").write_text("dirty\n", encoding="utf-8")

            self.assertEqual(2, run_consumer(consumer, source, "adopt"))

            self.assertFalse((consumer / "boundary.lock.json").exists())
            self.assertEqual((), status_paths(consumer))

    def test_adoption_rejects_invalid_source_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            source = temp / "not-boundary"
            fixture_consumer = source / "scripts" / "consumer.py"
            fixture_consumer.parent.mkdir(parents=True)
            fixture_consumer.write_text("fixture\n", encoding="utf-8")
            consumer = temp / "consumer"
            self._initialize_unadopted_project(consumer)

            self.assertEqual(2, run_consumer(consumer, source, "adopt"))

            self.assertFalse((consumer / "boundary.lock.json").exists())
            self.assertEqual((), status_paths(consumer))

    def test_fresh_clone_lifecycle_and_deliberate_upgrade(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            v1, source1 = make_source_checkout(temp / "boundary-v1", "v1")
            v2, source2 = make_source_checkout(temp / "boundary-v2", "v2")
            fixture = temp / "fixture"
            fixture.mkdir()
            initialize_fixture(fixture, v1)
            consumer = temp / "consumer"
            clone_fixture(fixture, consumer)

            self.assertEqual(0, run_consumer(consumer, source1, "install"))
            self.assertEqual(0, run_consumer(consumer, source1, "check"))
            provenance = json.loads(
                (
                    consumer
                    / ".specify"
                    / "boundary-runtime"
                    / "source-lock.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(v1.to_document(), provenance)
            self.assertNotIn(str(source1), json.dumps(provenance))
            for path in (
                "src/boundary",
                "skills",
                "adapters",
                "integration",
            ):
                self.assertFalse((consumer / path).exists())
            assert_no_boundary_generated_status(self, consumer)
            self.assertEqual(
                (".specify/shared-registry.json",),
                status_paths(consumer),
            )

            self.assertEqual(0, run_consumer(consumer, source1, "remove"))
            self.assertEqual((), status_paths(consumer))
            self.assertEqual(0, run_consumer(consumer, source1, "reinstall"))
            self.assertEqual(0, run_consumer(consumer, source1, "check"))
            assert_no_boundary_generated_status(self, consumer)

            self.assertEqual(0, run_consumer(consumer, source2, "upgrade"))
            self.assertEqual(v2, load_lock(consumer / "boundary.lock.json"))
            self.assertEqual(0, run_consumer(consumer, source2, "check"))
            self.assertEqual(2, run_consumer(consumer, source1, "check"))
            assert_no_boundary_generated_status(self, consumer)

    def test_revision_mismatch_leaves_fresh_clone_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            locked, _ = make_source_checkout(temp / "boundary-v1", "v1")
            _, other = make_source_checkout(temp / "boundary-v2", "v2")
            fixture = temp / "fixture"
            fixture.mkdir()
            initialize_fixture(fixture, locked)
            consumer = temp / "consumer"
            clone_fixture(fixture, consumer)

            self.assertEqual(2, run_consumer(consumer, other, "install"))

            self.assertEqual((), status_paths(consumer))
            self.assertFalse((consumer / ".agents").exists())
            self.assertFalse(
                (consumer / ".specify" / "boundary-runtime").exists()
            )

    def test_dirty_source_checkout_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            locked, source = make_source_checkout(temp / "boundary-v1", "v1")
            fixture = temp / "fixture"
            fixture.mkdir()
            initialize_fixture(fixture, locked)
            consumer = temp / "consumer"
            clone_fixture(fixture, consumer)
            (source / "dirty.txt").write_text("dirty\n", encoding="utf-8")

            self.assertEqual(2, run_consumer(consumer, source, "install"))
            self.assertEqual((), status_paths(consumer))

    def test_failed_upgrade_preserves_lock_without_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            v1, source1 = make_source_checkout(temp / "boundary-v1", "v1")
            _, broken = make_source_checkout(
                temp / "boundary-broken",
                "broken",
                fail_install=True,
            )
            fixture = temp / "fixture"
            fixture.mkdir()
            initialize_fixture(fixture, v1)
            consumer = temp / "consumer"
            clone_fixture(fixture, consumer)

            self.assertEqual(0, run_consumer(consumer, source1, "install"))
            self.assertEqual(2, run_consumer(consumer, broken, "upgrade"))
            self.assertEqual(v1, load_lock(consumer / "boundary.lock.json"))
            self.assertEqual(2, run_consumer(consumer, source1, "check"))

            installed = (
                consumer
                / ".specify"
                / "boundary-runtime"
                / "installed-version"
            )
            self.assertEqual(
                "broken\n",
                installed.read_text(encoding="utf-8"),
            )
            assert_no_boundary_generated_status(self, consumer)

    @staticmethod
    def _initialize_unadopted_project(root: Path) -> None:
        root.mkdir()
        (root / "app.txt").write_text("fixture\n", encoding="utf-8")
        run_git(root, "init", "-q")
        run_git(root, "config", "user.email", "tests@example.invalid")
        run_git(root, "config", "user.name", "Boundary Tests")
        run_git(root, "add", "-A")
        run_git(root, "commit", "-q", "-m", "unadopted consumer fixture")


if __name__ == "__main__":
    unittest.main()
