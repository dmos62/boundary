"""Real Spec Kit 1.0.10 Linux script-mode recovery coverage."""

from __future__ import annotations

import platform
import re
import shutil
import unittest

from install_real_cli_support import (
    REPO_ROOT,
    SPECKIT_VERSION,
    RealSpecKitFixtureMixin,
    run,
)


@unittest.skipUnless(platform.system() == "Linux", "Linux integration coverage")
class RealSpecKitLinuxRecoveryTests(
    RealSpecKitFixtureMixin,
    unittest.TestCase,
):
    @classmethod
    def setUpClass(cls):
        for command in ("bash", "git", "uv", "specify"):
            if shutil.which(command) is None:
                raise unittest.SkipTest(f"{command} is required")
        version = run(["specify", "--version"], cwd=REPO_ROOT)
        pattern = rf"(^|[^0-9]){re.escape(SPECKIT_VERSION)}([^0-9]|$)"
        if version.returncode != 0 or re.search(
            pattern, version.stdout + version.stderr
        ) is None:
            raise unittest.SkipTest(
                f"Spec Kit {SPECKIT_VERSION} must already be installed"
            )

    def setUp(self):
        self.set_up_real_cli_fixture()

    def tearDown(self):
        self.tear_down_real_cli_fixture()

    def test_saved_ps_project_recovers_to_shell(self):
        if shutil.which("pwsh"):
            self.skipTest("requires a Linux host without pwsh")

        source = self.source_checkout()
        project = self.project("recovery")
        initialized = run(
            [
                "specify",
                "init",
                "--here",
                "--force",
                "--non-interactive",
                "--ignore-agent-tools",
                "--integration",
                "codex",
                "--script",
                "ps",
            ],
            cwd=project,
            env=self.env,
        )
        self.assert_success(initialized)
        self.commit(project, "saved PowerShell Spec Kit project")
        self.adopt(project, source)

        gitignore_before = (project / ".specify/.gitignore").read_bytes()
        self.assert_tracked(project, ".specify/.gitignore")
        self.assert_tracked(project, ".specify/integration.json")

        self.write_tool("pwsh")
        installed = self.consumer(project, source, "install")
        self.assert_success(installed)
        (self.bin_dir / "pwsh").unlink()

        for command in ("install", "check"):
            failed = self.consumer(project, source, command)
            self.assertEqual(
                2,
                failed.returncode,
                failed.stdout + failed.stderr,
            )
            self.assertIn(
                "Spec Kit PowerShell script mode requires pwsh",
                failed.stderr,
            )
            self.assertEqual("ps", self.script_mode(project))

        powershell = project / ".specify/scripts/powershell"
        powershell_before = self.tree_snapshot(powershell)
        self.assertTrue(powershell_before)

        recovery_env = dict(self.env)
        recovery_env["BOUNDARY_SPECKIT_SCRIPT"] = "sh"
        recovered = self.consumer(
            project,
            source,
            "reinstall",
            env=recovery_env,
        )
        self.assert_success(recovered)
        checked = self.consumer(project, source, "check")
        self.assert_success(checked)

        self.assert_shell_mode(project)
        self.assertTrue(powershell.is_dir())
        self.assertEqual(powershell_before, self.tree_snapshot(powershell))
        self.assert_gitignore(project)
        self.assertEqual(
            gitignore_before,
            (project / ".specify/.gitignore").read_bytes(),
        )
        self.run_workflow_helper(project)

        status_paths = {
            line[3:]
            for line in self.status_lines(project)
            if len(line) >= 4
        }
        self.assertIn(".specify/init-options.json", status_paths)
        self.assertIn(".specify/extensions/.registry", status_paths)
        self.assertIn(".specify/presets/.registry", status_paths)

        manifests = {
            path
            for path in status_paths
            if path.startswith(".specify/integrations/")
            and path.endswith(".manifest.json")
        }
        bash_scripts = {
            path
            for path in status_paths
            if path.startswith(".specify/scripts/bash/")
        }
        core_skills = {
            path
            for path in status_paths
            if path.startswith(".agents/skills/speckit-")
            and not path.startswith(".agents/skills/speckit-boundary-")
        }
        self.assertTrue(manifests)
        self.assertTrue(bash_scripts)
        self.assertTrue(core_skills)

        shared_paths = {
            ".specify/.gitignore",
            ".specify/init-options.json",
            ".specify/integration.json",
            ".specify/extensions/.registry",
            ".specify/presets/.registry",
            *manifests,
            *bash_scripts,
            *core_skills,
        }
        for path in shared_paths:
            self.assert_not_ignored(project, path)

        boundary_generated = (
            ".agents/skills/boundary-",
            ".agents/skills/speckit-boundary-",
            ".specify/boundary-runtime/",
            ".specify/extensions/boundary/",
            ".specify/presets/boundary/",
            ".specify/workflows/overlays/speckit/boundary.yml",
        )
        self.assertFalse(
            any(
                path.startswith(boundary_path)
                for path in status_paths
                for boundary_path in boundary_generated
            )
        )
        self.assertFalse(
            any(
                path.startswith(".specify/scripts/powershell/")
                for path in status_paths
            )
        )


if __name__ == "__main__":
    unittest.main()
