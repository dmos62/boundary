"""Provider-neutral native operation authorization boundary."""

from .engine import (
    authorize_contract_evolution,
    authorize_implementation,
    is_native_contract_path,
)
from .git import (
    capture_dirty_path_states,
    capture_git_baseline,
    capture_git_head,
    path_state,
)
from .handoff import (
    AuthorizationHandoff,
    AuthorizationHandoffTarget,
    read_authorization_handoff,
)
from .identities import contract_graph_identity, effective_context_identity
from .model import (
    AuthorizationError,
    AuthorizedTarget,
    ChangeWriteSet,
    ContractEvolutionAuthorization,
    ContractEvolutionWriteSet,
    ImplementationAuthorization,
    TaskWriteSet,
    WriteSetError,
)
from .record import (
    CarriedForwardState,
    DirtyPathState,
    GitBaseline,
    OperationRecord,
    OperationTargetEvidence,
)
from .service import (
    authorize_contract_evolution_operation,
    authorize_implementation_operation,
)
from .storage import (
    OPERATION_EVIDENCE_UNAVAILABLE,
    archive_operation,
    check_operation_evidence_persistence,
    current_operation_path,
    operation_archive_path,
    read_current_operation,
    write_current_operation,
)

__all__ = [
    "AuthorizationError",
    "AuthorizationHandoff",
    "AuthorizationHandoffTarget",
    "AuthorizedTarget",
    "CarriedForwardState",
    "ChangeWriteSet",
    "ContractEvolutionAuthorization",
    "ContractEvolutionWriteSet",
    "DirtyPathState",
    "GitBaseline",
    "ImplementationAuthorization",
    "OPERATION_EVIDENCE_UNAVAILABLE",
    "OperationRecord",
    "OperationTargetEvidence",
    "TaskWriteSet",
    "WriteSetError",
    "archive_operation",
    "authorize_contract_evolution",
    "authorize_contract_evolution_operation",
    "authorize_implementation",
    "authorize_implementation_operation",
    "capture_dirty_path_states",
    "capture_git_baseline",
    "capture_git_head",
    "check_operation_evidence_persistence",
    "contract_graph_identity",
    "current_operation_path",
    "effective_context_identity",
    "is_native_contract_path",
    "operation_archive_path",
    "path_state",
    "read_authorization_handoff",
    "read_current_operation",
    "write_current_operation",
]
