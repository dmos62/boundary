"""Compact read-only handoff for current Boundary authorization state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .git import capture_git_head
from .record import OperationRecord
from .storage import read_current_operation


@dataclass(frozen=True, slots=True)
class AuthorizationHandoffTarget:
    """Compact historical evidence for one authorized operation target."""

    path: str
    owner: str | None
    effective_context_identity: str | None

    def to_document(self) -> dict[str, object]:
        value: dict[str, object] = {"path": self.path}
        if self.owner is not None:
            value["owner"] = self.owner
        if self.effective_context_identity is not None:
            value["effectiveContextIdentity"] = (
                self.effective_context_identity
            )
        return value


@dataclass(frozen=True, slots=True)
class AuthorizationHandoff:
    """Compact operation state suitable for coordinator-to-worker handoff."""

    operation_id: str
    change_id: str
    kind: str
    status: str
    selected_task_ids: tuple[str, ...]
    authorized_targets: tuple[AuthorizationHandoffTarget, ...]
    contract_graph_identity: str
    baseline_head: str | None
    current_head: str | None

    @property
    def head_matches_baseline(self) -> bool:
        """Return whether current HEAD still matches authorization-time HEAD."""

        return self.current_head == self.baseline_head

    def to_document(self) -> dict[str, object]:
        """Project this handoff into a stable compact document."""

        return {
            "schema": "boundary.authorization-handoff/v1",
            "operationId": self.operation_id,
            "changeId": self.change_id,
            "kind": self.kind,
            "status": self.status,
            "selectedTaskIds": list(self.selected_task_ids),
            "authorizedTargets": [
                target.to_document()
                for target in self.authorized_targets
            ],
            "contractGraphIdentity": self.contract_graph_identity,
            "git": {
                "baselineHead": self.baseline_head,
                "currentHead": self.current_head,
                "headMatchesBaseline": self.head_matches_baseline,
            },
        }


def read_authorization_handoff(
    repository_root: str | Path,
) -> AuthorizationHandoff | None:
    """Return compact current operation state without changing authority."""

    current = read_current_operation(repository_root)
    if current is None:
        return None

    current_head = capture_git_head(repository_root)
    return _handoff_from_record(current, current_head)


def _handoff_from_record(
    current: OperationRecord,
    current_head: str | None,
) -> AuthorizationHandoff:
    return AuthorizationHandoff(
        operation_id=current.operation_id,
        change_id=current.change_id,
        kind=current.kind,
        status=current.status,
        selected_task_ids=current.selected_task_ids,
        authorized_targets=tuple(
            AuthorizationHandoffTarget(
                path=target.path,
                owner=target.owner,
                effective_context_identity=(
                    target.effective_context_identity
                ),
            )
            for target in current.authorized_targets
        ),
        contract_graph_identity=current.contract_graph_identity,
        baseline_head=current.git_baseline.head,
        current_head=current_head,
    )
