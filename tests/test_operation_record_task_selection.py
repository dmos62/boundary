"""Tests for explicit task-selection evidence in operation records."""

from copy import deepcopy
import unittest

from boundary.authorization import (
    AuthorizationError,
    GitBaseline,
    OperationRecord,
    OperationTargetEvidence,
    TaskWriteSet,
)
from boundary.authorization.codec import operation_record_from_document


class OperationRecordTaskSelectionTests(unittest.TestCase):
    def test_valid_record_preserves_explicit_selected_task_ids(self) -> None:
        record = operation_record_from_document(_implementation_document())

        self.assertEqual(record.selected_task_ids, ("T001",))

    def test_valid_record_serializes_selected_task_ids_explicitly(self) -> None:
        record = operation_record_from_document(_implementation_document())

        self.assertEqual(record.to_document()["selectedTaskIds"], ["T001"])

    def test_missing_selected_task_ids_is_rejected(self) -> None:
        document = _implementation_document()
        del document["selectedTaskIds"]

        with self.assertRaisesRegex(
            AuthorizationError,
            "selectedTaskIds must be an array",
        ):
            operation_record_from_document(document)

    def test_empty_selected_task_ids_is_not_inferred_from_tasks(self) -> None:
        document = _implementation_document()
        document["selectedTaskIds"] = []

        with self.assertRaisesRegex(
            AuthorizationError,
            "selected task identities must match operation task evidence",
        ):
            operation_record_from_document(document)

    def test_inconsistent_selected_task_ids_is_rejected(self) -> None:
        document = _implementation_document()
        document["selectedTaskIds"] = ["T999"]

        with self.assertRaisesRegex(
            AuthorizationError,
            "selected task identities must match operation task evidence",
        ):
            operation_record_from_document(document)

    def test_authorized_targets_must_match_selected_task_writes(self) -> None:
        document = _implementation_document()
        document["authorizedTargets"][0]["path"] = "src/other.py"

        with self.assertRaisesRegex(
            AuthorizationError,
            "authorized targets must exactly match selected task writes",
        ):
            operation_record_from_document(document)

    def test_authorized_targets_must_preserve_selected_write_order(self) -> None:
        document = _implementation_document()
        document["tasks"][0]["writes"] = [
            "src/example.py",
            "src/other.py",
        ]
        document["authorizedTargets"] = [
            {
                "path": "src/other.py",
                "owner": "example-owner",
                "effectiveContextIdentity": "sha256:other-context",
            },
            {
                "path": "src/example.py",
                "owner": "example-owner",
                "effectiveContextIdentity": "sha256:context",
            },
        ]

        with self.assertRaisesRegex(
            AuthorizationError,
            "authorized targets must exactly match selected task writes",
        ):
            operation_record_from_document(document)

    def test_implementation_target_requires_owner_evidence(self) -> None:
        document = _implementation_document()
        del document["authorizedTargets"][0]["owner"]

        with self.assertRaisesRegex(
            AuthorizationError,
            "must include owner and effective context identity",
        ):
            operation_record_from_document(document)

    def test_implementation_target_requires_context_identity(self) -> None:
        document = _implementation_document()
        del document["authorizedTargets"][0]["effectiveContextIdentity"]

        with self.assertRaisesRegex(
            AuthorizationError,
            "must include owner and effective context identity",
        ):
            operation_record_from_document(document)

    def test_implementation_task_evidence_requires_a_write(self) -> None:
        document = _implementation_document()
        document["tasks"][0]["writes"] = []
        document["authorizedTargets"] = []

        with self.assertRaisesRegex(
            AuthorizationError,
            "must declare at least one write target",
        ):
            operation_record_from_document(document)

    def test_operation_record_does_not_infer_missing_selection(self) -> None:
        task = TaskWriteSet(
            order=0,
            task_id="T001",
            story=None,
            writes=("src/example.py",),
        )

        with self.assertRaisesRegex(
            ValueError,
            "selected task identities must match operation task evidence",
        ):
            OperationRecord(
                operation_id="operation-1",
                change_id="change-1",
                kind="implementation",
                tasks=(task,),
                authorized_targets=(
                    OperationTargetEvidence(
                        path="src/example.py",
                        owner="example-owner",
                        effective_context_identity="sha256:context",
                    ),
                ),
                contract_graph_identity="sha256:graph",
                git_baseline=GitBaseline(head=None),
            )


def _implementation_document() -> dict[str, object]:
    return deepcopy(
        {
            "schemaVersion": 1,
            "operationId": "operation-1",
            "changeId": "change-1",
            "kind": "implementation",
            "selectedTaskIds": ["T001"],
            "tasks": [
                {
                    "order": 0,
                    "id": "T001",
                    "story": None,
                    "writes": ["src/example.py"],
                }
            ],
            "authorizedTargets": [
                {
                    "path": "src/example.py",
                    "owner": "example-owner",
                    "effectiveContextIdentity": "sha256:context",
                }
            ],
            "contractGraphIdentity": "sha256:graph",
            "gitBaseline": {
                "head": None,
                "dirtyPathStates": [],
            },
            "carriedForward": [],
            "status": "authorized",
        }
    )


if __name__ == "__main__":
    unittest.main()
