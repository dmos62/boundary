"""Focused regression coverage for installed contract-evolution CLI entry."""

import json
from io import StringIO
from pathlib import Path
import subprocess
import tempfile
import unittest

from boundary.authorization import (
    AuthorizationError,
    ChangeWriteSet,
    TaskWriteSet,
    authorize_implementation_operation,
    read_current_operation,
)
from boundary.cli.main import main
from boundary.contracts import load_contract_graph
from boundary.context import resolve_target_context
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

    def test_evolution_establishes_exact_owner_before_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._repository(Path(directory))
            interface_path = "specs/005-dev-chrome-session/contracts/cli.md"
            sibling_path = "specs/005-dev-chrome-session/contracts/other.md"
            contract_path = "contracts/feature-005-interface.contract.md"
            change = ChangeWriteSet(
                "feature-005",
                (
                    TaskWriteSet(
                        order=0,
                        task_id="T026",
                        story="US1",
                        writes=(interface_path,),
                    ),
                ),
            )

            with self.assertRaises(AuthorizationError) as raised:
                authorize_implementation_operation(
                    root,
                    change,
                    selected_task_ids=("T026",),
                )
            self.assertEqual("UNOWNED_WRITE_TARGET", raised.exception.code)
            self.assertIsNone(read_current_operation(root))

            evolution_output = StringIO()
            result = main(
                [
                    "contracts",
                    "authorize",
                    "--change",
                    "feature-005",
                    contract_path,
                ],
                repository_root=root,
                stdout=evolution_output,
                stderr=StringIO(),
            )
            self.assertEqual(0, result)
            evolution = json.loads(evolution_output.getvalue())
            self.assertEqual([contract_path], evolution["authorizedTargets"])
            self.assertFalse((root / interface_path).exists())

            (root / contract_path).write_text(
                "---\n"
                "schema: boundary.contract/v1\n"
                "id: feature-005-interface\n"
                "owns:\n"
                f"  - {interface_path}\n"
                "---\n"
                "\n"
                "# Feature 005 CLI interface\n"
                "\n"
                "## Purpose\n"
                "\n"
                "Own the durable Feature 005 CLI interface contract.\n",
                encoding="utf-8",
            )

            check_output = StringIO()
            self.assertEqual(
                0,
                main(
                    ["contracts", "check"],
                    repository_root=root,
                    stdout=check_output,
                    stderr=StringIO(),
                ),
            )
            self.assertIn("contracts: ok", check_output.getvalue())

            graph = load_contract_graph(root)
            self.assertEqual(
                "feature-005-interface",
                resolve_target_context(graph, interface_path).owner_id,
            )
            self.assertIsNone(
                resolve_target_context(graph, sibling_path).owner_id
            )

            verified = finalize_operation_verification(root)
            self.assertEqual("verified", verified.status)
            self.assertEqual("contract-evolution", verified.kind)
            self.assertFalse((root / interface_path).exists())

            implementation = authorize_implementation_operation(
                root,
                change,
                selected_task_ids=("T026",),
            )
            self.assertEqual("implementation", implementation.kind)
            self.assertEqual(("T026",), implementation.selected_task_ids)
            self.assertNotEqual(
                evolution["operationId"],
                implementation.operation_id,
            )
            self.assertEqual(
                (interface_path,),
                tuple(
                    target.path
                    for target in implementation.authorized_targets
                ),
            )
            self.assertEqual(
                "feature-005-interface",
                implementation.authorized_targets[0].owner,
            )

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
