import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
SCRIPT_ROOT = REPOSITORY_ROOT / "integration" / "speckit" / "scripts"
for path in (SCRIPT_ROOT, SOURCE_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from adapter_gate import run_stage
from spec_kit_adapter import authorize_feature, verify_feature
from spec_kit_discovery import active_feature
from spec_kit_errors import SpecKitAdapterError
from task_projection import parse_tasks


def run_git(root: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


def write_contract(root: Path) -> None:
    path = root / "contracts" / "app.contract.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "---\n"
        "schema: boundary.contract/v1\n"
        "id: app\n"
        "owns:\n"
        "  - src/**\n"
        "applies_to: []\n"
        "depends_on: []\n"
        "---\n"
        "## Invariants\n\n"
        "- Application behavior remains explicit.\n",
        encoding="utf-8",
    )


class SpecKitProjectionTests(unittest.TestCase):
    def test_projects_only_dedicated_writes_metadata(self):
        tasks = parse_tasks(
            "# Tasks\n\n"
            "- [ ] T001 [US1] Mention `docs/advisory.md` in prose\n"
            "  Writes: `src/a.py` `src/b.py`\n"
            "- [ ] T002 [P] [US2] No implementation write yet\n"
        )

        self.assertEqual(("T001", "T002"), tuple(t.task_id for t in tasks))
        self.assertEqual(("US1", "US2"), tuple(t.story for t in tasks))
        self.assertEqual(
            ("src/a.py", "src/b.py"),
            tasks[0].writes,
        )
        self.assertEqual((), tasks[1].writes)

    def test_rejects_duplicate_writes_metadata(self):
        with self.assertRaisesRegex(
            SpecKitAdapterError,
            "duplicate Writes metadata",
        ):
            parse_tasks(
                "- [ ] T001 Work\n"
                "  Writes: `src/a.py`\n"
                "  Writes: `src/b.py`\n"
            )


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


@unittest.skipUnless(shutil.which("git"), "Git is required")
class SpecKitLifecycleTests(unittest.TestCase):
    def initialize(self, root: Path) -> Path:
        run_git(root, "init", "-q")
        run_git(root, "config", "user.email", "tests@example.invalid")
        run_git(root, "config", "user.name", "Boundary Tests")
        write_contract(root)

        source = root / "src"
        source.mkdir()
        (source / "a.py").write_text(
            "VALUE = 'before'\n",
            encoding="utf-8",
        )

        feature = root / "specs" / "001-change"
        feature.mkdir(parents=True)
        (feature / "tasks.md").write_text(
            "# Tasks\n\n"
            "- [ ] T001 [US1] Change application\n"
            "  Writes: `src/a.py`\n",
            encoding="utf-8",
        )

        run_git(root, "add", "-A")
        run_git(root, "commit", "-q", "-m", "baseline")
        return feature

    def test_authorizes_structured_scope_and_excludes_feature_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            feature = self.initialize(root)

            authorized = authorize_feature(root, feature, ("T001",))
            self.assertEqual("001-change", authorized.change_id)
            self.assertEqual(("T001",), authorized.selected_task_ids)
            self.assertEqual(
                ("src/a.py",),
                tuple(
                    target.path
                    for target in authorized.authorized_targets
                ),
            )

            (root / "src" / "a.py").write_text(
                "VALUE = 'after'\n",
                encoding="utf-8",
            )
            (feature / "progress.md").write_text(
                "host state\n",
                encoding="utf-8",
            )

            verified = verify_feature(root, feature)

        self.assertEqual("verified", verified.status)

    def test_status_projects_compact_authorization_handoff(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            feature = self.initialize(root)
            authorized = authorize_feature(root, feature, ("T001",))

            with mock.patch.dict(
                "os.environ",
                {"SPECIFY_FEATURE_DIRECTORY": str(feature)},
                clear=False,
            ):
                status = run_stage(root, "status")

        self.assertTrue(status["matchesActiveFeature"])
        handoff = status["authorizationState"]
        self.assertIsInstance(handoff, dict)
        assert isinstance(handoff, dict)
        self.assertEqual(
            "boundary.authorization-handoff/v1",
            handoff["schema"],
        )
        self.assertEqual(
            authorized.operation_id,
            handoff["operationId"],
        )
        self.assertEqual(["T001"], handoff["selectedTaskIds"])
        self.assertTrue(handoff["git"]["headMatchesBaseline"])


if __name__ == "__main__":
    unittest.main()
