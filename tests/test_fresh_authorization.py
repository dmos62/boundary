import tempfile
import unittest
from pathlib import Path

from boundary.authorization import (
    AuthorizationError,
    ChangeWriteSet,
    ContractEvolutionWriteSet,
    TaskWriteSet,
    authorize_contract_evolution,
    authorize_implementation,
)


def write_contract(
    root: Path,
    *,
    invariant: str = "Service behavior remains stable.",
) -> None:
    path = root / "contracts" / "auth.contract.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        "schema: boundary.contract/v1\n"
        "id: auth\n"
        "owns:\n"
        "  - src/auth/**\n"
        "applies_to: []\n"
        "depends_on: []\n"
        "---\n"
        "## Purpose\n\n"
        "Own authentication implementation.\n\n"
        "## Invariants\n\n"
        f"- {invariant}\n",
        encoding="utf-8",
    )


class FreshAuthorizationTests(unittest.TestCase):
    def change(self, path: str) -> ChangeWriteSet:
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

    def test_fresh_authorization_resolves_owner_and_context_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_contract(root)
            first = authorize_implementation(
                root,
                self.change("src/auth/service.ts"),
                selected_task_ids=("T001",),
            )

            write_contract(
                root,
                invariant="Changed canonical behavior remains stable.",
            )
            second = authorize_implementation(
                root,
                self.change("src/auth/service.ts"),
                selected_task_ids=("T001",),
            )

        self.assertEqual("auth", first.targets[0].owner_id)
        self.assertTrue(
            first.targets[0].effective_context_identity.startswith("sha256:")
        )
        self.assertNotEqual(
            first.targets[0].effective_context_identity,
            second.targets[0].effective_context_identity,
        )
        self.assertNotEqual(
            first.contract_graph_identity,
            second.contract_graph_identity,
        )

    def test_feature_003_shape_authorizes_only_selected_tasks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_contract(root)
            change = ChangeWriteSet(
                "003-desktop",
                (
                    TaskWriteSet(
                        0,
                        "T009",
                        "US1",
                        ("src/auth/clipboard.ts",),
                    ),
                    TaskWriteSet(
                        1,
                        "T012",
                        "US1",
                        ("src/auth/calibration.ts",),
                    ),
                ),
            )

            single = authorize_implementation(
                root,
                change,
                selected_task_ids=("T012",),
            )
            combined = authorize_implementation(
                root,
                change,
                selected_task_ids=("T012", "T009"),
            )

        self.assertEqual(("T012",), single.selected_task_ids)
        self.assertEqual(("src/auth/calibration.ts",), single.writes)
        self.assertEqual(("T009", "T012"), combined.selected_task_ids)
        self.assertEqual(
            ("src/auth/clipboard.ts", "src/auth/calibration.ts"),
            combined.writes,
        )

    def test_implementation_requires_one_unambiguous_owner(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_contract(root)
            with self.assertRaisesRegex(
                AuthorizationError,
                "no primary owner",
            ):
                authorize_implementation(
                    root,
                    self.change("docs/login.md"),
                    selected_task_ids=("T001",),
                )

    def test_implementation_and_contract_evolution_are_separate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_contract(root)

            with self.assertRaisesRegex(
                AuthorizationError,
                "may not modify native contracts",
            ):
                authorize_implementation(
                    root,
                    self.change("contracts/auth.contract.md"),
                    selected_task_ids=("T001",),
                )

            evolution = authorize_contract_evolution(
                root,
                ContractEvolutionWriteSet(
                    "001-login",
                    ("contracts/auth.contract.md",),
                ),
            )
            self.assertEqual(
                ("contracts/auth.contract.md",),
                evolution.targets,
            )

            with self.assertRaisesRegex(
                AuthorizationError,
                "only native contracts",
            ):
                authorize_contract_evolution(
                    root,
                    ContractEvolutionWriteSet(
                        "001-login",
                        ("src/auth/service.ts",),
                    ),
                )


if __name__ == "__main__":
    unittest.main()
