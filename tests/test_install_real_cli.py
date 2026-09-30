"""Real Spec Kit 1.0.10 Linux downstream install coverage."""

from __future__ import annotations

import json
import platform
import re
import shutil
import sys
import unittest

from install_real_cli_support import (
    REPO_ROOT,
    SPECKIT_VERSION,
    RealSpecKitFixtureMixin,
    run,
)


@unittest.skipUnless(platform.system() == "Linux", "Linux integration coverage")
class RealSpecKitLinuxInstallTests(
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

    def test_clean_install_uses_semantic_entrypoint_without_powershell(self):
        source = self.source_checkout()
        project = self.project("clean")
        self.adopt(project, source)

        installed = self.consumer(project, source, "install")
        self.assert_success(installed)
        checked = self.consumer(project, source, "check")
        self.assert_success(checked)

        self.assert_shell_mode(project)
        self.assert_gitignore(project)
        self.run_workflow_helper(project)

        launcher = project / ".boundary" / "bin" / "boundary"
        self.assertTrue(launcher.is_file())

        contract = project / "contracts" / "app.contract.md"
        contract.parent.mkdir()
        contract.write_text(
            "---\n"
            "schema: boundary.contract/v1\n"
            "id: downstream-app\n"
            "owns:\n"
            "  - app.txt\n"
            "---\n\n"
            "# Downstream App\n\n"
            "## Invariants\n\n"
            "- Fixture behavior remains explicit.\n",
            encoding="utf-8",
        )
        feature = project / "specs" / "001-runtime-check"
        feature.mkdir(parents=True)
        (feature / "tasks.md").write_text(
            "# Tasks\n\n"
            "- [ ] T001 Exercise adapter runtime selection\n"
            "  Writes: `app.txt`\n",
            encoding="utf-8",
        )
        self.commit(project, "add authorization fixture")

        (project / ".specify/feature.json").write_text(
            json.dumps(
                {"feature_directory": "specs/001-runtime-check"}
            ),
            encoding="utf-8",
        )
        pwsh = self.bin_dir / "pwsh"
        pwsh.write_text(
            "#!/bin/sh\n"
            "echo 'unexpected PowerShell invocation' >&2\n"
            "exit 97\n",
            encoding="utf-8",
        )
        pwsh.chmod(0o755)

        contracts = run(
            [str(launcher), "contracts", "check"],
            cwd=project,
            env=self.env,
        )
        self.assert_success(contracts)

        inspected = run(
            [str(launcher), "inspect", "app.txt"],
            cwd=project,
            env=self.env,
        )
        self.assert_success(inspected)
        self.assertIn("downstream-app", inspected.stdout)

        authorized = run(
            [
                str(launcher),
                "authorize",
                "--task",
                "T001",
            ],
            cwd=project,
            env=self.env,
        )
        self.assert_success(authorized)
        payload = json.loads(authorized.stdout)
        self.assertEqual("speckit", payload["adapter"])
        self.assertEqual(
            "specs/001-runtime-check",
            payload["feature"],
        )
        self.assertEqual(
            ["T001"],
            payload["operation"]["selectedTaskIds"],
        )

        status = run(
            [str(launcher), "status"],
            cwd=project,
            env=self.env,
        )
        self.assert_success(status)
        status_payload = json.loads(status.stdout)
        self.assertEqual("boundary.status/v2", status_payload["schema"])
        self.assertEqual(
            payload["operation"]["operationId"],
            status_payload["operation"]["operationId"],
        )
        self.assertEqual(
            ["T001"],
            status_payload["operation"]["selectedTaskIds"],
        )
        self.assertEqual(
            payload["operation"]["changeId"],
            status_payload["operation"]["changeId"],
        )
        self.assertTrue(status_payload["operation"]["authorizedTargets"])

        head = run(["git", "rev-parse", "HEAD"], cwd=project)
        self.assert_success(head)
        self.assertEqual(
            head.stdout.strip(),
            status_payload["freshness"]["currentHead"],
        )
        self.assertTrue(status_payload["freshness"]["headMatchesBaseline"])


if __name__ == "__main__":
    unittest.main()
