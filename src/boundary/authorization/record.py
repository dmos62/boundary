"""Versioned atomic operation-record model."""

from dataclasses import dataclass, replace
from uuid import uuid4

from .model import (
    ContractEvolutionAuthorization,
    ImplementationAuthorization,
    TaskWriteSet,
)
from .record_document import operation_record_to_document
from .record_validation import (
    validate_nonempty as _validate_nonempty,
    validate_operation_id as _validate_operation_id,
    validate_path as _validate_path,
    validate_unique_paths as _validate_unique_paths,
)


@dataclass(frozen=True, slots=True)
class DirtyPathState:
    """Exact identity of one dirty Git path."""

    path: str
    state: str

    def __post_init__(self) -> None:
        _validate_path(self.path)
        _validate_nonempty(self.state, "path state")


@dataclass(frozen=True, slots=True)
class GitBaseline:
    """Git state captured immediately before operation evidence is stored."""

    head: str | None
    dirty_path_states: tuple[DirtyPathState, ...] = ()

    def __post_init__(self) -> None:
        if self.head is not None:
            _validate_nonempty(self.head, "Git HEAD")
        _validate_unique_paths(
            self.dirty_path_states,
            "Git baseline dirty path",
        )


@dataclass(frozen=True, slots=True)
class CarriedForwardState:
    """Verified predecessor output adopted by one successor epoch."""

    path: str
    state: str
    operation_id: str

    def __post_init__(self) -> None:
        _validate_path(self.path)
        _validate_nonempty(self.state, "carried-forward state")
        _validate_operation_id(self.operation_id)


@dataclass(frozen=True, slots=True)
class OperationTargetEvidence:
    """Historical authorization evidence for one exact operation target."""

    path: str
    owner: str | None = None
    effective_context_identity: str | None = None

    def __post_init__(self) -> None:
        _validate_path(self.path)
        if self.owner is not None:
            _validate_nonempty(self.owner, "target owner")
        if self.effective_context_identity is not None:
            _validate_nonempty(
                self.effective_context_identity,
                "effective context identity",
            )


@dataclass(frozen=True, slots=True)
class OperationRecord:
    """One versioned historical document for one authorized operation."""

    operation_id: str
    change_id: str
    kind: str
    tasks: tuple[TaskWriteSet, ...]
    authorized_targets: tuple[OperationTargetEvidence, ...]
    contract_graph_identity: str
    git_baseline: GitBaseline
    carried_forward: tuple[CarriedForwardState, ...] = ()
    verification_final_states: tuple[DirtyPathState, ...] = ()
    status: str = "authorized"
    selected_task_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_operation_id(self.operation_id)
        _validate_nonempty(self.change_id, "change id")
        _validate_nonempty(
            self.contract_graph_identity,
            "contract graph identity",
        )
        if self.kind not in {"implementation", "contract-evolution"}:
            raise ValueError(f"unsupported operation kind: {self.kind!r}")
        if self.status not in {"authorized", "verified"}:
            raise ValueError(f"unsupported operation status: {self.status!r}")
        if self.status == "authorized" and self.verification_final_states:
            raise ValueError(
                "authorized operation cannot contain final verification states"
            )

        self._validate_task_selection()
        _validate_unique_paths(
            self.authorized_targets,
            "authorized target",
        )
        _validate_unique_paths(
            self.carried_forward,
            "carried-forward path",
        )
        _validate_unique_paths(
            self.verification_final_states,
            "verification final path",
        )

        target_paths = {target.path for target in self.authorized_targets}
        for item in self.carried_forward:
            if item.path not in target_paths:
                raise ValueError(
                    "carried-forward path is not an authorized target: "
                    f"{item.path}"
                )
        for item in self.verification_final_states:
            if item.path not in target_paths:
                raise ValueError(
                    "verification final path is not an authorized target: "
                    f"{item.path}"
                )

    def _validate_task_selection(self) -> None:
        if self.kind == "contract-evolution":
            if self.tasks or self.selected_task_ids:
                raise ValueError(
                    "contract-evolution operation must not contain task selection"
                )
            return

        task_ids = tuple(task.task_id for task in self.tasks)
        if not task_ids or any(task_id is None for task_id in task_ids):
            raise ValueError(
                "implementation operation must contain selected task identities"
            )

        canonical_ids = tuple(
            task_id for task_id in task_ids if task_id is not None
        )
        selected = tuple(self.selected_task_ids) or canonical_ids
        if selected != canonical_ids:
            raise ValueError(
                "selected task identities must match operation task evidence"
            )
        if len(selected) != len(set(selected)):
            raise ValueError("selected task identities must be unique")
        for task_id in selected:
            _validate_nonempty(task_id, "selected task id")
        object.__setattr__(self, "selected_task_ids", selected)

    def mark_verified(
        self,
        final_states: tuple[DirtyPathState, ...],
    ) -> "OperationRecord":
        """Return the closed verified form of this operation epoch."""

        return replace(
            self,
            status="verified",
            verification_final_states=tuple(final_states),
        )

    def to_document(self) -> dict[str, object]:
        """Project the record into its stable version-1 JSON document."""

        return operation_record_to_document(self)


def new_operation_id() -> str:
    """Create one filesystem-safe opaque operation identifier."""

    return uuid4().hex


def implementation_record(
    authorization: ImplementationAuthorization,
    baseline: GitBaseline,
    *,
    operation_id: str | None = None,
    carried_forward: tuple[CarriedForwardState, ...] = (),
) -> OperationRecord:
    """Build an operation record from fresh implementation authorization."""

    return OperationRecord(
        operation_id=operation_id or new_operation_id(),
        change_id=authorization.change_id,
        kind="implementation",
        tasks=authorization.tasks,
        authorized_targets=tuple(
            OperationTargetEvidence(
                path=target.path,
                owner=target.owner_id,
                effective_context_identity=target.effective_context_identity,
            )
            for target in authorization.targets
        ),
        contract_graph_identity=authorization.contract_graph_identity,
        git_baseline=baseline,
        carried_forward=carried_forward,
        selected_task_ids=authorization.selected_task_ids,
    )


def contract_evolution_record(
    authorization: ContractEvolutionAuthorization,
    baseline: GitBaseline,
    *,
    operation_id: str | None = None,
    carried_forward: tuple[CarriedForwardState, ...] = (),
) -> OperationRecord:
    """Build an isolated contract-evolution operation record."""

    return OperationRecord(
        operation_id=operation_id or new_operation_id(),
        change_id=authorization.change_id,
        kind="contract-evolution",
        tasks=(),
        authorized_targets=tuple(
            OperationTargetEvidence(path=path) for path in authorization.targets
        ),
        contract_graph_identity=authorization.contract_graph_identity,
        git_baseline=baseline,
        carried_forward=carried_forward,
    )
