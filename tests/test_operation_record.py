from boundary.cli.integration import update_managed_ignore
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from boundary.pre_change import (
    PreChangeError,
    ChangeWriteSet,
    ContractEvolutionWriteSet,
    TaskWriteSet,
    open_contract_operation,
    open_implementation_operation,
    current_operation_path,
)
from boundary.post_change import close_verified_operation


class OperationRecordTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def initialize_repository(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name).resolve()
        self.git(root, "init")
        update_managed_ignore(root, True)
        self.git(root, "config", "user.name", "Boundary Test")
        self.git(root, "config", "user.email", "boundary@example.test")

        contract = root / "contracts/auth.contract.md"
        contract.parent.mkdir(parents=True)
        contract.write_text(
            "---\n"
            "schema: boundary.contract/v1\n"
            "id: auth\n"
            "owns:\n"
            "  - src/auth/**\n"
            "applies_to: []\n"
            "depends_on: []\n"
            "---\n"
            "## Invariants\n\n"
            "- Authentication writes remain owned here.\n",
            encoding="utf-8",
        )
        files = {
            "src/auth/service.ts": "export const value = 1;\n",
            "docs/note.md": "note\n",
            "docs/old.md": "old\n",
        }
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.git(root, "add", ".")
        self.git(
            root,
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-m",
            "baseline",
        )
        return temporary, root

    def implementation_change(self, path: str = "src/auth/service.ts"):
        return ChangeWriteSet(
            "001-login",
            (
                TaskWriteSet(
                    0,
                    "T001",
                    "US1",
                    (path,),
                ),
            ),
        )

    def test_atomic_record_contains_fresh_authority_and_git_baseline(self):
        temporary, root = self.initialize_repository()
        with temporary:
            (root / "docs/note.md").write_text(
                "staged change\n",
                encoding="utf-8",
            )
            self.git(root, "add", "docs/note.md")
            (root / "docs/old.md").unlink()

            record = open_implementation_operation(
                root,
                self.implementation_change(),
                selected_task_ids=("T001",),
                operation_id="operation-1",
            )
            path = current_operation_path(root)
            document = json.loads(path.read_text(encoding="utf-8"))
            head = self.git(root, "rev-parse", "HEAD")

        self.assertEqual("operation-1", record.operation_id)
        self.assertEqual("implementation", document["kind"])
        self.assertEqual(["T001"], document["selectedTaskIds"])
        self.assertEqual(["T001"], [item["id"] for item in document["tasks"]])
        self.assertEqual(head, document["gitBaseline"]["head"])
        self.assertEqual(
            ["docs/note.md", "docs/old.md"],
            [
                item["path"]
                for item in document["gitBaseline"]["dirtyPathStates"]
            ],
        )
        states = {
            item["path"]: item["state"]
            for item in document["gitBaseline"]["dirtyPathStates"]
        }
        self.assertTrue(states["docs/note.md"].startswith("file:sha256:"))
        self.assertTrue(states["docs/old.md"].startswith("missing:sha256:"))
        self.assertEqual(
            "auth",
            document["allowedTargets"][0]["owner"],
        )
        self.assertTrue(
            document["allowedTargets"][0][
                "effectiveContextIdentity"
            ].startswith("sha256:")
        )

    def test_failed_reauthorization_preserves_prior_successful_record(self):
        temporary, root = self.initialize_repository()
        with temporary:
            open_implementation_operation(
                root,
                self.implementation_change(),
                selected_task_ids=("T001",),
                operation_id="operation-1",
            )
            path = current_operation_path(root)
            before = path.read_bytes()

            with self.assertRaisesRegex(
                PreChangeError,
                "OPERATION_OPEN",
            ):
                open_implementation_operation(
                    root,
                    self.implementation_change("docs/unowned.md"),
                    selected_task_ids=("T001",),
                    operation_id="operation-2",
                )

            self.assertEqual(before, path.read_bytes())

    def test_atomic_replace_failure_preserves_prior_record(self):
        temporary, root = self.initialize_repository()
        with temporary:
            open_implementation_operation(
                root,
                self.implementation_change(),
                selected_task_ids=("T001",),
                operation_id="operation-1",
            )
            close_verified_operation(
                root,
                operation_id="operation-1",
            )
            path = current_operation_path(root)
            before = path.read_bytes()

            with mock.patch(
                "boundary.operation.storage.os.replace",
                side_effect=OSError("replace failed"),
            ):
                with self.assertRaisesRegex(
                    PreChangeError,
                    "atomic operation evidence",
                ):
                    open_implementation_operation(
                        root,
                        self.implementation_change(),
                        selected_task_ids=("T001",),
                        operation_id="operation-2",
                    )

            self.assertEqual(before, path.read_bytes())

    def test_contract_evolution_record_is_a_separate_operation_kind(self):
        temporary, root = self.initialize_repository()
        with temporary:
            record = open_contract_operation(
                root,
                ContractEvolutionWriteSet(
                    "001-login",
                    ("contracts/auth.contract.md",),
                ),
                operation_id="contracts-1",
            )
            document = json.loads(
                current_operation_path(root).read_text(encoding="utf-8")
            )

        self.assertEqual("contract-evolution", record.kind)
        self.assertEqual([], document["selectedTaskIds"])
        self.assertEqual([], document["tasks"])
        self.assertEqual(
            [{"path": "contracts/auth.contract.md"}],
            document["allowedTargets"],
        )


if __name__ == "__main__":
    unittest.main()
