"""Regressions for contract-evolution closure through the public CLI."""

import json
from io import StringIO
from pathlib import Path
import subprocess
import tempfile
import unittest

from boundary.authorization import read_current_operation
from boundary.cli import main


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


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def write(root: Path, path: str, contents: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(contents, encoding="utf-8")


def cli(root: Path, *args: str) -> tuple[int, dict, str]:
    output = StringIO()
    errors = StringIO()
    code = main(
        args,
        repository_root=root,
        stdout=output,
        stderr=errors,
    )
    return code, json.loads(output.getvalue()), errors.getvalue()


class ContractEvolutionVerificationCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "tests@example.invalid")
        git(self.root, "config", "user.name", "Boundary Tests")
        write(self.root, "contracts/app.contract.md", CONTRACT)
        write(
            self.root,
            "specs/006-example/plan.md",
            "# Plan\n\nOriginal plan.\n",
        )
        write(
            self.root,
            "specs/006-example/tasks.md",
            "# Tasks\n\nOriginal tasks.\n",
        )
        write(self.root, "src/app.py", "VALUE = 1\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "baseline")

    def authorize(self) -> dict:
        code, result, errors = cli(
            self.root,
            "contracts",
            "authorize",
            "--change",
            "006-example",
            "contracts/app.contract.md",
        )
        self.assertEqual(0, code, errors)
        self.assertEqual("authorized", result["status"])
        return result

    def test_cli_closes_contract_evolution_with_feature_bookkeeping(self) -> None:
        authorized = self.authorize()
        write(
            self.root,
            "contracts/app.contract.md",
            CONTRACT + "\n## Interfaces\n\n- Expose app interface.\n",
        )
        write(
            self.root,
            "specs/006-example/plan.md",
            "# Plan\n\nRefined plan.\n",
        )
        write(
            self.root,
            "specs/006-example/tasks.md",
            "# Tasks\n\nRefined tasks.\n",
        )

        code, result, errors = cli(self.root, "verify")

        self.assertEqual(0, code, errors)
        self.assertEqual("boundary.lifecycle-result/v1", result["schema"])
        self.assertEqual("verify", result["stage"])
        self.assertEqual("verified", result["status"])
        self.assertEqual(authorized["operationId"], result["operationId"])
        self.assertEqual([], result["diagnostics"])
        current = read_current_operation(self.root)
        self.assertEqual("verified", current.status)
        self.assertEqual("contract-evolution", current.kind)

    def test_unauthorized_contract_write_is_blocked(self) -> None:
        self.authorize()
        write(
            self.root,
            "contracts/other.contract.md",
            CONTRACT.replace("id: app", "id: other").replace(
                "src/**", "other/**"
            ),
        )

        code, result, errors = cli(self.root, "verify")

        self.assertEqual(2, code, errors)
        self.assertEqual("blocked", result["status"])
        self.assertEqual("UNDECLARED_WRITE", result["code"])
        self.assertEqual(
            "authorized",
            read_current_operation(self.root).status,
        )

    def test_contract_evolution_cannot_authorize_source_writes(self) -> None:
        self.authorize()
        write(self.root, "src/app.py", "VALUE = 2\n")

        code, result, errors = cli(self.root, "verify")

        self.assertEqual(2, code, errors)
        self.assertEqual("blocked", result["status"])
        self.assertEqual("OPERATION_KIND_VIOLATION", result["code"])
        self.assertEqual(
            "authorized",
            read_current_operation(self.root).status,
        )

    def test_failed_verification_retains_stable_diagnostics(self) -> None:
        self.authorize()
        write(self.root, "src/app.py", "VALUE = 2\n")

        first = cli(self.root, "verify")
        second = cli(self.root, "verify")

        self.assertEqual(2, first[0])
        self.assertEqual(first[1], second[1])
        self.assertEqual("verify", first[1]["stage"])
        self.assertEqual(
            "OPERATION_KIND_VIOLATION",
            first[1]["diagnostics"][0]["code"],
        )
        self.assertEqual(
            "authorized",
            read_current_operation(self.root).status,
        )

    def test_cli_help_describes_both_verification_kinds(self) -> None:
        from boundary.cli import build_parser

        help_text = build_parser().format_help()
        self.assertIn("Persistent-contract evolution:", help_text)
        self.assertIn("boundary contracts check", help_text)
        self.assertIn("boundary verify", help_text)
        self.assertIn("either operation kind", help_text)


if __name__ == "__main__":
    unittest.main()
