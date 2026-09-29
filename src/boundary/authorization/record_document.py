"""Stable JSON projection for native Boundary operation records."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .record import (
        DirtyPathState,
        OperationRecord,
        OperationTargetEvidence,
    )


def operation_record_to_document(
    record: "OperationRecord",
) -> dict[str, object]:
    """Project one operation record into its version-1 document."""

    document: dict[str, object] = {
        "schemaVersion": 1,
        "operationId": record.operation_id,
        "changeId": record.change_id,
        "kind": record.kind,
        "selectedTaskIds": list(record.selected_task_ids),
        "tasks": [
            {
                "order": task.order,
                "id": task.task_id,
                "story": task.story,
                "writes": list(task.writes),
            }
            for task in record.tasks
        ],
        "authorizedTargets": [
            _target_document(target)
            for target in record.authorized_targets
        ],
        "contractGraphIdentity": record.contract_graph_identity,
        "gitBaseline": {
            "head": record.git_baseline.head,
            "dirtyPathStates": _state_documents(
                record.git_baseline.dirty_path_states
            ),
        },
        "carriedForward": [
            {
                "path": item.path,
                "state": item.state,
                "operationId": item.operation_id,
            }
            for item in record.carried_forward
        ],
        "status": record.status,
    }
    if record.status == "verified":
        document["verification"] = {
            "finalPathStates": _state_documents(
                record.verification_final_states
            ),
        }
    return document


def _target_document(
    target: "OperationTargetEvidence",
) -> dict[str, object]:
    value: dict[str, object] = {"path": target.path}
    if target.owner is not None:
        value["owner"] = target.owner
    if target.effective_context_identity is not None:
        value["effectiveContextIdentity"] = (
            target.effective_context_identity
        )
    return value


def _state_documents(
    states: tuple["DirtyPathState", ...],
) -> list[dict[str, str]]:
    return [
        {"path": item.path, "state": item.state}
        for item in states
    ]
