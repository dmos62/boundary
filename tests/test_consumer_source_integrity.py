"""Tests for invoking Boundary source-checkout validation."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from consumer_source import (  # noqa: E402
    BoundarySourceError,
    load_source_checkout,
)


@unittest.skipUnless(shutil.which("git"), "Git is required")
class ConsumerSourceCheckoutTests(unittest.TestCase):
    def test_accepts_clean_checkout_and_reports_exact_head(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = self._initialize_source(root)
            expected = self._git(root, "rev-parse", "HEAD").strip()

            source = load_source_checkout(consumer)

            self.assertEqual(root.resolve(), source.root)
            self.assertEqual(expected, source.revision)

    def test_rejects_dirty_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = self._initialize_source(root)
            (root / "dirty.txt").write_text("dirty\n", encoding="utf-8")

            with self.assertRaisesRegex(
                BoundarySourceError,
                "must be clean",
            ):
                load_source_checkout(consumer)

    def test_rejects_non_git_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = root / "scripts" / "consumer.py"
            consumer.parent.mkdir()
            consumer.write_text("fixture\n", encoding="utf-8")

            with self.assertRaisesRegex(
                BoundarySourceError,
                "not a Git worktree",
            ):
                load_source_checkout(consumer)

    def test_requires_consumer_at_checkout_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._initialize_source(root)
            nested = root / "nested" / "scripts" / "consumer.py"
            nested.parent.mkdir(parents=True)
            nested.write_text("fixture\n", encoding="utf-8")

            with self.assertRaisesRegex(
                BoundarySourceError,
                "source checkout root",
            ):
                load_source_checkout(nested)

    @classmethod
    def _initialize_source(cls, root: Path) -> Path:
        consumer = root / "scripts" / "consumer.py"
        consumer.parent.mkdir(parents=True)
        consumer.write_text("fixture\n", encoding="utf-8")
        cls._git(root, "init", "-q")
        cls._git(root, "config", "user.email", "tests@example.invalid")
        cls._git(root, "config", "user.name", "Boundary Tests")
        cls._git(root, "add", "-A")
        cls._git(root, "commit", "-q", "-m", "source fixture")
        return consumer

    @staticmethod
    def _git(root: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        return result.stdout


if __name__ == "__main__":
    unittest.main()
