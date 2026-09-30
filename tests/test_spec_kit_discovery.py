import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = REPOSITORY_ROOT / "integration" / "speckit" / "scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from spec_kit_discovery import active_feature
from spec_kit_errors import SpecKitAdapterError


class SpecKitFeatureDiscoveryTests(unittest.TestCase):
    def discovery_fixture(self, root: Path, mode: str) -> Path:
        feature = root / "specs" / "001-change"
        feature.mkdir(parents=True)

        specify = root / ".specify"
        specify.mkdir()
        (specify / "init-options.json").write_text(
            json.dumps({"script": mode}),
            encoding="utf-8",
        )

        relative_scripts = {
            "sh": "bash/check-prerequisites.sh",
            "ps": "powershell/check-prerequisites.ps1",
            "py": "python/check_prerequisites.py",
        }
        script = specify / "scripts" / relative_scripts[mode]
        script.parent.mkdir(parents=True)
        script.write_text("", encoding="utf-8")
        return feature

    def assert_discovery_command(self, mode: str) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            feature = self.discovery_fixture(root, mode)
            scripts = root / ".specify" / "scripts"
            commands = {
                "sh": [
                    "bash",
                    str(scripts / "bash/check-prerequisites.sh"),
                    "--json",
                    "--paths-only",
                ],
                "ps": [
                    "pwsh",
                    str(scripts / "powershell/check-prerequisites.ps1"),
                    "-Json",
                    "-PathsOnly",
                ],
                "py": [
                    sys.executable,
                    str(scripts / "python/check_prerequisites.py"),
                    "--json",
                    "--paths-only",
                ],
            }
            expected = commands[mode]
            completed = subprocess.CompletedProcess(
                expected,
                0,
                stdout=json.dumps({"FEATURE_DIR": str(feature)}),
                stderr="",
            )

            with mock.patch(
                "spec_kit_discovery.subprocess.run",
                return_value=completed,
            ) as invoked:
                resolved, relative = active_feature(root)

            self.assertEqual(feature, resolved)
            self.assertEqual("specs/001-change", relative)
            invoked.assert_called_once_with(
                expected,
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_uses_configured_shell_runtime(self):
        self.assert_discovery_command("sh")

    def test_uses_configured_powershell_runtime(self):
        self.assert_discovery_command("ps")

    def test_uses_configured_python_runtime(self):
        self.assert_discovery_command("py")

    def test_rejects_unsupported_configured_runtime(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            specify = root / ".specify"
            specify.mkdir()
            (specify / "init-options.json").write_text(
                json.dumps({"script": "other"}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                SpecKitAdapterError,
                "unsupported configured Spec Kit script mode",
            ):
                active_feature(root)


if __name__ == "__main__":
    unittest.main()
