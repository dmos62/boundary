import json
import tempfile
import unittest
from pathlib import Path

from preset_test_install_support import (
    assert_resolved_workflow,
    installed_overlay_text,
)
from preset_test_support import (
    INSTALLER_PATH,
    INSTALLED_BOUNDARY_RUNTIME,
    INSTALLED_RUNTIME_PATH,
    active_integration,
    archive_source,
    command_available,
    init_project,
    require_success,
    run_command,
    run_installed_gate,
    write_consumer_fixture,
)


BOUNDARY_SKILLS = (
    "boundary-scope",
    "boundary-implement",
    "boundary-contracts",
)


@unittest.skipUnless(
    command_available("bash")
    and command_available("specify")
    and command_available("codex")
    and command_available("git")
    and command_available("uv"),
    "Bash, Spec Kit, Codex, Git, and uv are required for distribution tests",
)
class DistributionInstallTests(unittest.TestCase):
    def _skill_bytes(self, root: Path) -> dict[str, bytes]:
        return {
            skill: (
                root / ".agents" / "skills" / skill / "SKILL.md"
            ).read_bytes()
            for skill in BOUNDARY_SKILLS
        }

    def _assert_adapter_installed(self, root: Path) -> None:
        self.assertTrue((root / ".specify" / "extensions" / "boundary").is_dir())
        self.assertTrue((root / ".specify" / "presets" / "boundary").is_dir())
        self.assertTrue((root / INSTALLED_RUNTIME_PATH).is_file())
        self.assertTrue((root / INSTALLED_BOUNDARY_RUNTIME).is_file())

        for skill in BOUNDARY_SKILLS:
            with self.subTest(skill=skill):
                path = root / ".agents" / "skills" / skill / "SKILL.md"
                self.assertTrue(path.is_file())
                content = path.read_text(encoding="utf-8")
                self.assertIn(f"name: {skill}", content)
                self.assertIn(f"# {skill}", content)

        for command in (
            "speckit-boundary-authorize",
            "speckit-boundary-verify",
        ):
            self.assertTrue(
                (root / ".agents" / "skills" / command / "SKILL.md").is_file()
            )

        overlay = run_command(
            root,
            "specify",
            "workflow",
            "overlay",
            "list",
            "speckit",
        )
        require_success(self, overlay)
        self.assertIn("boundary", overlay.stdout)
        overlay_text = installed_overlay_text(root)
        self.assertIn(str(INSTALLED_RUNTIME_PATH), overlay_text)
        self.assertNotIn("integration/speckit/scripts/adapter_gate.py", overlay_text)

    def _install_local_archive(self, root: Path, archive: Path):
        return run_command(
            root,
            "bash",
            str(INSTALLER_PATH),
            "--source",
            str(archive),
        )

    def test_local_install_switches_codex_and_supports_remove_reinstall(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            init_project(self, root, integration="claude")

            first = run_command(
                root,
                "bash",
                str(INSTALLER_PATH),
                "--source",
                str(INSTALLER_PATH.parents[1]),
            )
            require_success(self, first)
            self.assertEqual("codex", active_integration(root))
            self._assert_adapter_installed(root)

            check = run_command(root, "bash", str(INSTALLER_PATH), "--check")
            require_success(self, check)

            removed = run_command(root, "bash", str(INSTALLER_PATH), "--remove")
            require_success(self, removed)
            self.assertFalse(
                (root / ".specify" / "extensions" / "boundary").exists()
            )
            self.assertFalse((root / ".specify" / "presets" / "boundary").exists())
            self.assertFalse((root / ".specify" / "boundary-runtime").exists())
            for skill in BOUNDARY_SKILLS:
                self.assertFalse(
                    (root / ".agents" / "skills" / skill).exists()
                )

            second = run_command(
                root,
                "bash",
                str(INSTALLER_PATH),
                "--source",
                str(INSTALLER_PATH.parents[1]),
            )
            require_success(self, second)
            self._assert_adapter_installed(root)

    def test_local_archive_runs_native_boundary_lifecycle(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            init_project(self, root)
            feature_dir = write_consumer_fixture(self, root)
            archive = archive_source(root)

            installed = self._install_local_archive(root, archive)
            require_success(self, installed)
            archive.unlink()
            self._assert_adapter_installed(root)
            skill_bytes = self._skill_bytes(root)

            self.assertFalse((root / "integration" / "speckit").exists())
            self.assertFalse((root / "integration" / "speckit-preset").exists())
            self.assertFalse((root / "adapters").exists())
            self.assertFalse((root / "skills").exists())
            self.assertFalse((root / "src" / "boundary").exists())
            self.assertFalse((root / "scripts" / "bootstrap.sh").exists())

            resolved = run_command(
                root,
                "specify",
                "workflow",
                "resolve",
                "speckit",
            )
            require_success(self, resolved)
            assert_resolved_workflow(self, resolved.stdout)

            authorize = run_installed_gate(
                root,
                feature_dir,
                "authorize",
                task_ids=("T001",),
            )
            require_success(self, authorize)
            authorization = json.loads(authorize.stdout)
            operation = authorization["operation"]
            self.assertEqual("implementation", operation["kind"])
            self.assertEqual("authorized", operation["status"])
            self.assertEqual(["T001"], operation["selectedTaskIds"])
            self.assertEqual(
                ["src/app.py"],
                [item["path"] for item in operation["authorizedTargets"]],
            )

            (root / "src" / "app.py").write_text(
                'VALUE = "after"\n',
                encoding="utf-8",
            )
            (feature_dir / "progress.md").write_text(
                "generated host state\n",
                encoding="utf-8",
            )

            verify = run_installed_gate(root, feature_dir, "verify")
            require_success(self, verify)
            verification = json.loads(verify.stdout)
            self.assertEqual("verified", verification["operation"]["status"])
            self.assertEqual(skill_bytes, self._skill_bytes(root))
