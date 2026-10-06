from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mise_distribution_support import (
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
    and command_available("uv")
    and command_available("specify")
    and command_available("codex"),
    "Git, mise, uv, Spec Kit, and Codex are required",
)
class MiseIntegrationLifecycleTests(unittest.TestCase):
    def test_installed_cli_manages_generated_integration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            source, _ = make_boundary_source(base)
            project = base / "consumer"
            write_downstream_project(project, source)
            env = mise_env(project, base / "mise")

            require_success(self, run_command(project, "mise", "lock", env=env))
            require_success(
                self,
                run_command(project, "mise", "install", "--locked", env=env),
            )

            which = run_command(project, "mise", "which", "boundary", env=env)
            require_success(self, which)
            installed_boundary = Path(which.stdout.strip()).resolve()
            mise_data = Path(env["MISE_DATA_DIR"]).resolve()
            self.assertTrue(installed_boundary.is_file())
            self.assertTrue(installed_boundary.is_relative_to(mise_data))
            self.assertFalse(
                installed_boundary.is_relative_to(project.resolve())
            )

            help_result = self._boundary(project, env, "--help")
            require_success(self, help_result)
            self.assertIn("integration", help_result.stdout)
            self.assertFalse((project / ".boundary").exists())
            self.assertFalse((project / ".specify" / "boundary-runtime").exists())
            self.assertFalse((project / "boundary.lock.json").exists())

            require_success(
                self,
                self._boundary(project, env, "integration", "install"),
            )
            require_success(
                self,
                self._boundary(project, env, "integration", "check"),
            )

            stale_lock_references = self._find_text_references(
                project,
                (".agents", ".specify"),
                "boundary.lock.json",
            )
            self.assertEqual([], stale_lock_references)

            workflow_overlay = (
                project
                / ".specify"
                / "workflows"
                / "overlays"
                / "speckit"
                / "boundary.yml"
            ).read_text(encoding="utf-8")
            self.assertIn("mise install --locked", workflow_overlay)

            status = run_command(
                project,
                "git",
                "status",
                "--short",
                "--untracked-files=all",
                env=env,
            )
            require_success(self, status)
            self.assertIn(".specify/init-options.json", status.stdout)
            self.assertNotIn(".agents/skills/boundary-scope/", status.stdout)
            self.assertNotIn(".specify/extensions/boundary/", status.stdout)

            skill = (
                project
                / ".agents"
                / "skills"
                / "boundary-scope"
                / "SKILL.md"
            )
            skill.write_text("stale\n", encoding="utf-8")
            stale = self._boundary(project, env, "integration", "check")
            self.assertEqual(2, stale.returncode)
            self.assertIn("stale", stale.stderr.lower())

            require_success(
                self,
                self._boundary(project, env, "integration", "install"),
            )
            require_success(
                self,
                self._boundary(project, env, "integration", "check"),
            )

            require_success(
                self,
                self._boundary(project, env, "integration", "remove"),
            )
            self.assertFalse(
                (project / ".agents" / "skills" / "boundary-scope").exists()
            )
            self.assertFalse(
                (project / ".specify" / "extensions" / "boundary").exists()
            )
            self.assertTrue((project / ".specify" / "init-options.json").is_file())
            self.assertTrue((project / ".specify" / "integration.json").is_file())

    @staticmethod
    def _boundary(
        project: Path,
        env: dict[str, str],
        *args: str,
    ):
        return run_command(
            project,
            "mise",
            "exec",
            "--",
            "boundary",
            *args,
            env=env,
        )

    @staticmethod
    def _find_text_references(
        project: Path,
        roots: tuple[str, ...],
        needle: str,
    ) -> list[str]:
        matches: list[str] = []
        for relative_root in roots:
            root = project / relative_root
            for path in sorted(root.rglob("*")):
                if not path.is_file():
                    continue
                try:
                    content = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                if needle in content:
                    matches.append(path.relative_to(project).as_posix())
        return matches


if __name__ == "__main__":
    unittest.main()
