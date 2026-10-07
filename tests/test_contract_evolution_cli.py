"""Focused regression coverage for installed contract-evolution CLI entry."""

import json
from io import StringIO
from pathlib import Path
import subprocess
import tempfile
import unittest

from boundary.authorization import read_current_operation
from boundary.cli.main import main
from boundary.verification import finalize_operation_verification


class ContractEvolutionCliTests(unittest.TestCase):
    def test_authorize_persists_isolated_contract_operation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(Path(directory))
            output = StringIO()
            errors = StringIO()

            result = main(
                [
                    "contracts",
                    "authorize",
                    "--change",
                    "feature-005",
                    "contracts/system.contract.md",
                ],
                repository_root=root,
                stdout=output,
                stderr=errors,
            )

            self.assertEqual(0, result)
            self.assertEqual("", errors.getvalue())
            document = json.loads(output.getvalue())
            self.assertEqual("boundary.lifecycle-result/v1", document["schema"])
            self.assertEqual("authorized", document["status"])
            self.assertEqual("authorize", document["stage"])
            self.assertEqual("feature-005", document["changeId"])
            self.assertEqual(
                ["contracts/system.contract.md"],
                document["authorizedTargets"],
            )
            self.assertEqual([], document["diagnostics"])
            self.assertNotIn("selectedTaskIds", document)

            current = read_current_operation(root)
            self.assertIsNotNone(current)
            assert current is not None
            self.assertEqual("contract-evolution", current.kind)
            self.assertEqual((), current.tasks)
            self.assertEqual((), current.selected_task_ids)
            self.assertEqual(
                ("contracts/system.contract.md",),
                tuple(target.path for target in current.authorized_targets),
            )

    def test_fresh_authorization_requires_predecessor_closure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(Path(directory))
            arguments = [
                "contracts",
                "authorize",
                "--change",
                "feature-005",
                "contracts/system.contract.md",
            ]

            first_output = StringIO()
            self.assertEqual(
                0,
                main(
                    arguments,
                    repository_root=root,
                    stdout=first_output,
                    stderr=StringIO(),
                ),
            )
            first = json.loads(first_output.getvalue())

            blocked_output = StringIO()
            result = main(
                arguments,
                repository_root=root,
                stdout=blocked_output,
                stderr=StringIO(),
            )

            self.assertEqual(2, result)
            blocked = json.loads(blocked_output.getvalue())
            self.assertEqual("blocked", blocked["status"])
            self.assertEqual("OPERATION_NOT_VERIFIED", blocked["code"])
            self.assertEqual(first["operationId"], blocked["operationId"])
            self.assertEqual(
                "OPERATION_NOT_VERIFIED",
                blocked["diagnostics"][0]["code"],
            )

            verified = finalize_operation_verification(root)
            self.assertEqual("verified", verified.status)

            successor_output = StringIO()
            self.assertEqual(
                0,
                main(
                    arguments,
                    repository_root=root,
                    stdout=successor_output,
                    stderr=StringIO(),
                ),
            )
            successor = json.loads(successor_output.getvalue())
            self.assertNotEqual(
                first["operationId"],
                successor["operationId"],
            )

    def test_authorize_rejects_ordinary_project_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(Path(directory))
            output = StringIO()

            result = main(
                [
                    "contracts",
                    "authorize",
                    "--change",
                    "feature-005",
                    "docs/spec.md",
                ],
                repository_root=root,
                stdout=output,
                stderr=StringIO(),
            )

            self.assertEqual(2, result)
            document = json.loads(output.getvalue())
            self.assertEqual("blocked", document["status"])
            self.assertEqual("OPERATION_KIND_VIOLATION", document["code"])
            self.assertIsNone(read_current_operation(root))

    def _repository(self, root: Path) -> Path:
        self._git(root, "init", "-q")
        self._git(root, "config", "user.email", "boundary@example.invalid")
        self._git(root, "config", "user.name", "Boundary Tests")

        contracts = root / "contracts"
        contracts.mkdir()
        (contracts / "system.contract.md").write_text(
            "---\n"
            "schema: boundary.contract/v1\n"
            "id: system\n"
            "owns:\n"
            "  - src/**\n"
            "---\n"
            "\n"
            "# System\n"
            "\n"
            "## Purpose\n"
            "\n"
            "Own application source.\n",
            encoding="utf-8",
        )
        self._git(root, "add", ".")
        self._git(root, "commit", "-qm", "baseline")
        return root

    def _git(self, root: Path, *arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
