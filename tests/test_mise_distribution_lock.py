from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mise_distribution_support import (
    advance_boundary_source,
    command_available,
    make_boundary_source,
    mise_env,
    require_success,
    run_command,
    write_downstream_project,
)


@unittest.skipUnless(
    command_available("git")
    and command_available("mise")
    and command_available("uv"),
    "Git, mise, and uv are required for mise distribution tests",
)
class MiseGitLockTests(unittest.TestCase):
    def test_locked_install_preserves_source_identity_until_bump(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            source, first_commit = make_boundary_source(base)
            project = base / "consumer"
            write_downstream_project(project, source)

            first_env = mise_env(project, base / "mise-a")
            require_success(self, run_command(project, "mise", "lock", env=first_env))
            lock_path = project / "mise.lock"
            first_lock = lock_path.read_text(encoding="utf-8")
            self.assertIn(first_commit, first_lock)
            self.assertNotIn("uv = {", first_lock)
            lock_sidecars = project / ".mise" / "locks"
            self.assertFalse(
                lock_sidecars.exists()
                and any(lock_sidecars.rglob("uv.lock"))
            )

            require_success(
                self,
                run_command(
                    project,
                    "mise",
                    "install",
                    "--locked",
                    env=first_env,
                ),
            )
            first_identity = run_command(
                project,
                "mise",
                "exec",
                "--",
                "boundary-test-source-id",
                env=first_env,
            )
            require_success(self, first_identity)
            self.assertEqual("source-a", first_identity.stdout.strip())

            second_commit = advance_boundary_source(source)
            self.assertNotEqual(first_commit, second_commit)

            reinstall_env = mise_env(project, base / "mise-b")
            require_success(
                self,
                run_command(
                    project,
                    "mise",
                    "install",
                    "--locked",
                    env=reinstall_env,
                ),
            )
            locked_identity = run_command(
                project,
                "mise",
                "exec",
                "--",
                "boundary-test-source-id",
                env=reinstall_env,
            )
            require_success(self, locked_identity)
            self.assertEqual("source-a", locked_identity.stdout.strip())
            self.assertEqual(first_lock, lock_path.read_text(encoding="utf-8"))

            upgrade_env = mise_env(project, base / "mise-c")
            require_success(
                self,
                run_command(
                    project,
                    "mise",
                    "lock",
                    "--bump",
                    env=upgrade_env,
                ),
            )
            upgraded_lock = lock_path.read_text(encoding="utf-8")
            self.assertIn(second_commit, upgraded_lock)
            self.assertNotEqual(first_lock, upgraded_lock)
            self.assertNotIn("uv = {", upgraded_lock)

            require_success(
                self,
                run_command(
                    project,
                    "mise",
                    "install",
                    "--locked",
                    env=upgrade_env,
                ),
            )
            upgraded_identity = run_command(
                project,
                "mise",
                "exec",
                "--",
                "boundary-test-source-id",
                env=upgrade_env,
            )
            require_success(self, upgraded_identity)
            self.assertEqual("source-b", upgraded_identity.stdout.strip())


if __name__ == "__main__":
    unittest.main()
