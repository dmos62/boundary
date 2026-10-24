"""Versioned atomic operation-record model."""

from dataclasses import dataclass, replace
from uuid import uuid4

from boundary.pre_change.model import (
    ContractScope,
    ImplementationScope,
    TaskWriteSet,
)
from .record_document import operation_record_to_document
from .record_validation import (
    validate_implementation_record_authority as _validate_implementation_record_authority,
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
    """Historical operation evidence for one exact operation target."""

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
    allowed_targets: tuple[OperationTargetEvidence, ...]
    contract_graph_identity: str
    git_baseline: GitBaseline
    carried_forward: tuple[CarriedForwardState, ...] = ()
    verified_final_states: tuple[DirtyPathState, ...] = ()
    status: str = "open"
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
        if self.status not in {"open", "verified", "abandoned"}:
            raise ValueError(f"unsupported operation status: {self.status!r}")
        if self.status in {"open", "abandoned"} and self.verified_final_states:
            raise ValueError(
                "unverified operation cannot contain final states"
            )

        self._validate_task_selection()
        _validate_unique_paths(
            self.allowed_targets,
            "authorized target",
        )
        if self.kind == "implementation":
            _validate_implementation_record_authority(
                self.tasks,
                self.allowed_targets,
            )
        _validate_unique_paths(
            self.carried_forward,
            "carried-forward path",
        )
        _validate_unique_paths(
            self.verified_final_states,
            "verified final path",
        )

        target_paths = {target.path for target in self.allowed_targets}
        for item in self.carried_forward:
            if item.path not in target_paths:
                raise ValueError(
                    "carried-forward path is not an authorized target: "
                    f"{item.path}"
                )
        for item in self.verified_final_states:
            if item.path not in target_paths:
                raise ValueError(
                    "verified final path is not an authorized target: "
                    f"{item.path}"
                )

    def _validate_task_selection(self) -> None:
        selected = tuple(self.selected_task_ids)
        if self.kind == "contract-evolution":
            if self.tasks or selected:
                raise ValueError(
                    "contract-evolution operation must not contain task selection"
                )
            object.__setattr__(self, "selected_task_ids", selected)
            return

        task_ids = tuple(task.task_id for task in self.tasks)
        if not task_ids or any(task_id is None for task_id in task_ids):
            raise ValueError(
                "implementation operation must contain selected task identities"
            )

        canonical_ids = tuple(
            task_id for task_id in task_ids if task_id is not None
        )
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
            verified_final_states=tuple(final_states),
        )

    def mark_abandoned(self) -> "OperationRecord":
        """Return the closed, explicitly unverified form."""
        if self.status != "open":
            raise ValueError("only an open operation may be abandoned")
        return replace(self, status="abandoned")

    def to_document(self) -> dict[str, object]:
        """Project the record into its stable version-1 JSON document."""

        return operation_record_to_document(self)


def new_operation_id() -> str:
    """Create one filesystem-safe opaque operation identifier."""

    return uuid4().hex


def implementation_record(
    authorization: ImplementationScope,
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
        allowed_targets=tuple(
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
    authorization: ContractScope,
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
        allowed_targets=tuple(
            OperationTargetEvidence(path=path) for path in authorization.targets
        ),
        contract_graph_identity=authorization.contract_graph_identity,
        git_baseline=baseline,
        carried_forward=carried_forward,
        selected_task_ids=(),
    )
