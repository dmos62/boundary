import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_HOST = REPO_ROOT / "scripts" / "install-host.sh"


class InstallHostScriptModeTests(unittest.TestCase):
    def run_host_case(self, body: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["INSTALL_HOST"] = str(INSTALL_HOST)
            return subprocess.run(
                ["bash", "-c", textwrap.dedent(body)],
                cwd=tmp,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_clean_project_leaves_script_selection_to_speckit(self) -> None:
        result = self.run_host_case(
            r'''
            set -euo pipefail
            ACTIVE_INTEGRATION=codex
            SPECKIT_SCRIPT_OVERRIDE=""
            fail() { printf 'fail: %s\n' "$*" >&2; exit 1; }
            selected_speckit_script_type() { printf 'sh\n'; }
            require_speckit_script_runtime() { :; }
            specify() {
              printf '%s\n' "$*"
              mkdir -p .specify
            }
            source "$INSTALL_HOST"
            ensure_codex_project
            '''
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("init --here --force --non-interactive", result.stdout)
        self.assertIn("--integration codex", result.stdout)
        self.assertNotIn("--script", result.stdout)

    def test_existing_script_mode_is_preserved_without_override(self) -> None:
        result = self.run_host_case(
            r'''
            set -euo pipefail
            mkdir -p .specify
            ACTIVE_INTEGRATION=codex
            SPECKIT_SCRIPT_OVERRIDE=""
            fail() { printf 'fail: %s\n' "$*" >&2; exit 1; }
            active_integration() { printf 'codex\n'; }
            selected_speckit_script_type() { printf 'ps\n'; }
            require_speckit_script_runtime() { :; }
            specify() { printf 'unexpected specify call: %s\n' "$*" >&2; exit 9; }
            source "$INSTALL_HOST"
            active_integration() { printf 'codex\n'; }
            ensure_codex_project
            '''
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_integration_switch_does_not_force_script_mode(self) -> None:
        result = self.run_host_case(
            r'''
            set -euo pipefail
            mkdir -p .specify
            ACTIVE_INTEGRATION=codex
            SPECKIT_SCRIPT_OVERRIDE=""
            fail() { printf 'fail: %s\n' "$*" >&2; exit 1; }
            selected_speckit_script_type() { printf 'sh\n'; }
            require_speckit_script_runtime() { :; }
            specify() { printf '%s\n' "$*"; }
            source "$INSTALL_HOST"
            active_integration() { printf 'claude\n'; }
            ensure_codex_project
            '''
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "integration switch codex")

    def test_boundary_does_not_hard_code_powershell_mode(self) -> None:
        for relative_path in ("scripts/bootstrap.sh", "scripts/install-host.sh"):
            content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            self.assertNotIn("--script ps", content, relative_path)

    def test_explicit_override_uses_supported_upgrade_lifecycle(self) -> None:
        result = self.run_host_case(
            r'''
            set -euo pipefail
            mkdir -p .specify
            ACTIVE_INTEGRATION=codex
            SPECKIT_SCRIPT_OVERRIDE=sh
            printf 'ps\n' > script-mode
            fail() { printf 'fail: %s\n' "$*" >&2; exit 1; }
            require_speckit_script_runtime() { :; }
            specify() {
              printf '%s\n' "$*"
              printf 'sh\n' > script-mode
            }
            source "$INSTALL_HOST"
            active_integration() { printf 'codex\n'; }
            selected_speckit_script_type() { cat script-mode; }
            ensure_codex_project
            '''
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "integration upgrade codex --force --script sh",
        )

    def test_matching_override_does_not_refresh_integration(self) -> None:
        result = self.run_host_case(
            r'''
            set -euo pipefail
            mkdir -p .specify
            ACTIVE_INTEGRATION=codex
            SPECKIT_SCRIPT_OVERRIDE=sh
            fail() { printf 'fail: %s\n' "$*" >&2; exit 1; }
            selected_speckit_script_type() { printf 'sh\n'; }
            require_speckit_script_runtime() { :; }
            specify() { printf 'unexpected specify call: %s\n' "$*" >&2; exit 9; }
            source "$INSTALL_HOST"
            active_integration() { printf 'codex\n'; }
            ensure_codex_project
            '''
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
