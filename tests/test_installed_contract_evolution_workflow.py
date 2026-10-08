"""End-to-end contract-evolution verification through the installed executable."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


CONTRACT_PATH = "contracts/app.contract.md"
CHANGE_ID = "006-example"

CONTRACT = """---
schema: boundary.contract/v1
id: app
owns:
  - src/**
---

# App

## Invariants

- Application behavior remains explicit.
"""


def run_command(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def write(root: Path, path: str, contents: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(contents, encoding="utf-8")


@unittest.skipUnless(
    shutil.which("boundary"),
    "installed boundary executable required",
)
class InstalledContractEvolutionWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

        for args in (
            ("init", "-q"),
            ("config", "user.email", "tests@example.invalid"),
            ("config", "user.name", "Boundary Tests"),
        ):
            result = run_command(self.root, "git", *args)
            self.assertEqual(0, result.returncode, result.stderr)

        write(self.root, CONTRACT_PATH, CONTRACT)
        write(self.root, f"specs/{CHANGE_ID}/plan.md", "# Plan\n")
        write(
            self.root,
            f"specs/{CHANGE_ID}/tasks.md",
            "# Tasks\n\n"
            "- [ ] T001 Implement the application change\n"
            "  Writes: `src/app.py`\n",
        )
        write(self.root, "src/app.py", "VALUE = 1\n")

        for args in (("add", "-A"), ("commit", "-qm", "baseline")):
            result = run_command(self.root, "git", *args)
            self.assertEqual(0, result.returncode, result.stderr)

    def boundary(self, *args: str) -> tuple[int, dict, str]:
        result = run_command(self.root, "boundary", *args)
        try:
            document = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.fail(
                f"boundary {' '.join(args)} emitted invalid JSON: "
                f"{exc}\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )
        return result.returncode, document, result.stderr

    def current_operation(self) -> dict:
        result = run_command(
            self.root,
            "git",
            "rev-parse",
            "--absolute-git-dir",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        path = Path(result.stdout.strip()) / "boundary/current.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def authorize(self) -> dict:
        code, result, errors = self.boundary(
            "contracts",
            "authorize",
            "--change",
            CHANGE_ID,
            CONTRACT_PATH,
        )
        self.assertEqual(0, code, errors)
        self.assertEqual("boundary.lifecycle-result/v1", result["schema"])
        self.assertEqual("authorized", result["status"])
        self.assertEqual([CONTRACT_PATH], result["authorizedTargets"])
        self.assertEqual([], result["diagnostics"])
        return result

    def test_installed_cli_closes_evolution_with_active_bookkeeping(self) -> None:
        authorized = self.authorize()

        write(
            self.root,
            CONTRACT_PATH,
            CONTRACT + "\n## Interfaces\n\n- Expose the application interface.\n",
        )
        write(
            self.root,
            f"specs/{CHANGE_ID}/plan.md",
            "# Plan\n\nUpdated planning information.\n",
        )
        write(
            self.root,
            f"specs/{CHANGE_ID}/tasks.md",
            "# Tasks\n\n"
            "- [ ] T001 Implement the revised application change\n"
            "  Writes: `src/app.py`\n",
        )
        write(
            self.root,
            ".specify/feature-state.json",
            '{"feature": "006-example"}\n',
        )

        check = run_command(self.root, "boundary", "contracts", "check")
        self.assertEqual(0, check.returncode, check.stderr)
        self.assertIn("contracts: ok", check.stdout)

        code, verified, errors = self.boundary("verify")
        self.assertEqual(0, code, errors)
        self.assertEqual("boundary.lifecycle-result/v1", verified["schema"])
        self.assertEqual("verify", verified["stage"])
        self.assertEqual("verified", verified["status"])
        self.assertEqual(authorized["operationId"], verified["operationId"])
        self.assertEqual(CHANGE_ID, verified["changeId"])
        self.assertEqual([], verified["diagnostics"])

        operation = self.current_operation()
        self.assertEqual("contract-evolution", operation["kind"])
        self.assertEqual("verified", operation["status"])
        self.assertEqual(authorized["operationId"], operation["operationId"])

        code, handoff, errors = self.boundary("status")
        self.assertEqual(0, code, errors)
        self.assertEqual("contract-evolution", handoff["kind"])
        self.assertEqual("verified", handoff["status"])

    def test_installed_cli_blocks_ordinary_implementation_writes(self) -> None:
        self.authorize()
        write(self.root, "src/app.py", "VALUE = 2\n")

        code, result, errors = self.boundary("verify")

        self.assertEqual(2, code, errors)
        self.assertEqual("blocked", result["status"])
        self.assertEqual("verify", result["stage"])
        self.assertEqual("OPERATION_KIND_VIOLATION", result["code"])
        self.assertEqual(
            "OPERATION_KIND_VIOLATION",
            result["diagnostics"][0]["code"],
        )
        self.assertEqual("authorized", self.current_operation()["status"])

    def test_installed_cli_blocks_unauthorized_contract_writes(self) -> None:
        self.authorize()
        write(
            self.root,
            "contracts/other.contract.md",
            CONTRACT.replace("id: app", "id: other").replace(
                "src/**", "other/**"
            ),
        )

        code, result, errors = self.boundary("verify")

        self.assertEqual(2, code, errors)
        self.assertEqual("blocked", result["status"])
        self.assertEqual("UNDECLARED_WRITE", result["code"])
        self.assertEqual("authorized", self.current_operation()["status"])

    def test_installed_cli_does_not_exclude_other_feature_writes(self) -> None:
        self.authorize()
        write(
            self.root,
            "specs/007-unrelated/plan.md",
            "# Unauthorized feature plan\n",
        )

        code, result, errors = self.boundary("verify")

        self.assertEqual(2, code, errors)
        self.assertEqual("blocked", result["status"])
        self.assertEqual("OPERATION_KIND_VIOLATION", result["code"])
        self.assertEqual("authorized", self.current_operation()["status"])


if __name__ == "__main__":
    unittest.main()
