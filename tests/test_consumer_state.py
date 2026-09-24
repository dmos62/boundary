"""Focused tests for downstream generated-state bookkeeping."""

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

from consumer_state import (  # noqa: E402
    ConsumerStateError,
    EXCLUDE_BEGIN,
    EXCLUDE_END,
    GENERATED_EXCLUDES,
    require_local_excludes,
    update_local_excludes,
)


@unittest.skipUnless(shutil.which("git"), "Git is required")
class ConsumerLocalExcludeTests(unittest.TestCase):
    def test_managed_block_preserves_unrelated_excludes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._init_git(root)
            exclude = root / ".git" / "info" / "exclude"
            exclude.write_text(
                "# project-local exclusions\n/custom-cache/\n",
                encoding="utf-8",
            )

            update_local_excludes(root, enabled=True)
            require_local_excludes(root)

            self.assertEqual(
                [
                    "# project-local exclusions",
                    "/custom-cache/",
                    "",
                    EXCLUDE_BEGIN,
                    *GENERATED_EXCLUDES,
                    EXCLUDE_END,
                ],
                exclude.read_text(encoding="utf-8").splitlines(),
            )

            update_local_excludes(root, enabled=False)
            self.assertEqual(
                "# project-local exclusions\n/custom-cache/\n",
                exclude.read_text(encoding="utf-8"),
            )

    def test_malformed_managed_block_is_not_rewritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._init_git(root)
            exclude = root / ".git" / "info" / "exclude"
            original = (
                "# project-local exclusions\n"
                f"{EXCLUDE_BEGIN}\n"
                "/stale-boundary-path/\n"
            )
            exclude.write_text(original, encoding="utf-8")

            with self.assertRaisesRegex(
                ConsumerStateError,
                "malformed",
            ):
                update_local_excludes(root, enabled=False)

            self.assertEqual(
                original,
                exclude.read_text(encoding="utf-8"),
            )

    def test_health_check_requires_entries_inside_managed_block(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._init_git(root)
            exclude = root / ".git" / "info" / "exclude"
            exclude.write_text(
                "\n".join(
                    (
                        EXCLUDE_BEGIN,
                        EXCLUDE_END,
                        *GENERATED_EXCLUDES,
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ConsumerStateError,
                "missing or stale",
            ):
                require_local_excludes(root)

    @staticmethod
    def _init_git(root: Path) -> None:
        result = subprocess.run(
            ["git", "init", "-q"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
