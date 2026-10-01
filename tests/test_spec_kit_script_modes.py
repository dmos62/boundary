"""Focused regressions for Spec Kit script-mode integration behavior."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from boundary_host.discovery import active_feature
from boundary_host.errors import IntegrationError
from boundary_host.host_install import _ensure_codex_project
from boundary_host.host_runtime import require_script_runtime, script_override


class SpecKitScriptModeTests(unittest.TestCase):
    def test_active_feature_uses_configured_prerequisite_runner(self) -> None:
        cases = (
            (
                "sh",
                "bash",
                Path("bash") / "check-prerequisites.sh",
            ),
            (
                "ps",
                "pwsh",
                Path("powershell") / "check-prerequisites.ps1",
            ),
            (
                "py",
                sys.executable,
                Path("python") / "check_prerequisites.py",
            ),
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            feature = root / "specs" / "001-example"
            feature.mkdir(parents=True)
            options = root / ".specify" / "init-options.json"
            options.parent.mkdir(parents=True)

            for mode, launcher, relative_script in cases:
                with self.subTest(mode=mode):
                    options.write_text(
                        json.dumps({"script": mode}),
                        encoding="utf-8",
                    )
                    script = root / ".specify" / "scripts" / relative_script
                    script.parent.mkdir(parents=True, exist_ok=True)
                    script.write_text("fixture\n", encoding="utf-8")
                    result = subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout=json.dumps({"FEATURE_DIR": str(feature)}),
                        stderr="",
                    )

                    with (
                        patch.dict(os.environ, {}, clear=True),
                        patch(
                            "boundary_host.discovery.subprocess.run",
                            return_value=result,
                        ) as run,
                    ):
                        resolved, relative = active_feature(root)

                    self.assertEqual(feature, resolved)
                    self.assertEqual("specs/001-example", relative)
                    command = run.call_args.args[0]
                    self.assertEqual(launcher, command[0])
                    self.assertEqual(str(script), command[1])
                    if mode == "sh":
                        self.assertNotIn("pwsh", command)

    def test_runtime_prerequisites_follow_selected_mode(self) -> None:
        with patch(
            "boundary_host.host_runtime.require_command"
        ) as require:
            require_script_runtime("sh")
            require.assert_called_once_with("bash")

        with patch(
            "boundary_host.host_runtime.require_command"
        ) as require:
            require_script_runtime("ps")
            require.assert_called_once_with("pwsh")

        with patch(
            "boundary_host.host_runtime.require_command"
        ) as require:
            require_script_runtime("py")
            require.assert_not_called()

    def test_script_override_is_explicit_and_validated(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(script_override())

        for mode in ("sh", "ps", "py"):
            with self.subTest(mode=mode):
                with patch.dict(
                    os.environ,
                    {"BOUNDARY_SPECKIT_SCRIPT": mode},
                    clear=True,
                ):
                    self.assertEqual(mode, script_override())

        with patch.dict(
            os.environ,
            {"BOUNDARY_SPECKIT_SCRIPT": "invalid"},
            clear=True,
        ):
            with self.assertRaises(IntegrationError):
                script_override()

    def test_fresh_project_does_not_force_script_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()

            with (
                patch(
                    "boundary_host.host_install.run"
                ) as run,
                patch(
                    "boundary_host.host_install.selected_script_mode",
                    return_value="sh",
                ),
                patch(
                    "boundary_host.host_install.require_script_runtime"
                ) as require_runtime,
            ):
                _ensure_codex_project(root, None)

            command = run.call_args.args[1]
            self.assertEqual(
                ["specify", "init"],
                command[:2],
            )
            self.assertNotIn("--script", command)
            require_runtime.assert_called_once_with("sh")

    def test_existing_mode_is_preserved_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / ".specify").mkdir()

            with (
                patch(
                    "boundary_host.host_install.active_integration",
                    return_value="codex",
                ),
                patch(
                    "boundary_host.host_install.selected_script_mode",
                    return_value="sh",
                ),
                patch(
                    "boundary_host.host_install.run"
                ) as run,
                patch(
                    "boundary_host.host_install.require_script_runtime"
                ) as require_runtime,
            ):
                _ensure_codex_project(root, None)

            run.assert_not_called()
            require_runtime.assert_called_once_with("sh")

    def test_mode_transition_uses_host_upgrade_and_keeps_old_variant(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / ".specify").mkdir()
            inactive = (
                root
                / ".specify"
                / "scripts"
                / "powershell"
                / "legacy.ps1"
            )
            inactive.parent.mkdir(parents=True)
            inactive.write_text("fixture\n", encoding="utf-8")

            with (
                patch(
                    "boundary_host.host_install.active_integration",
                    return_value="codex",
                ),
                patch(
                    "boundary_host.host_install.selected_script_mode",
                    side_effect=("ps", "sh"),
                ),
                patch(
                    "boundary_host.host_install.run"
                ) as run,
                patch(
                    "boundary_host.host_install.require_script_runtime"
                ) as require_runtime,
            ):
                _ensure_codex_project(root, "sh")

            run.assert_called_once_with(
                root,
                [
                    "specify",
                    "integration",
                    "upgrade",
                    "codex",
                    "--force",
                    "--script",
                    "sh",
                ],
            )
            require_runtime.assert_called_once_with("sh")
            self.assertTrue(inactive.is_file())


if __name__ == "__main__":
    unittest.main()
