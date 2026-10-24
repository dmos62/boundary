"""Pre-change request resolution and operation opening."""

from .model import (
    PreChangeError, ChangeWriteSet, ContractEvolutionWriteSet,
    TaskWriteSet, WriteSetError, ImplementationScope, ContractScope,
    ResolvedTarget,
)
from .engine import resolve_implementation_scope, resolve_contract_scope, is_native_contract_path
from .service import open_implementation_operation, open_contract_operation
from boundary.operation.git import capture_git_baseline, capture_git_head, capture_dirty_path_states, path_state
from boundary.operation.record import OperationRecord, DirtyPathState, GitBaseline, CarriedForwardState, OperationTargetEvidence
from boundary.operation.storage import (
    read_current_operation, write_current_operation, current_operation_path,
    operation_archive_path, check_operation_evidence_persistence,
    archive_operation, OPERATION_EVIDENCE_UNAVAILABLE,
)
from boundary.operation.handoff import read_operation_status, OperationStatus, OperationStatusTarget
from boundary.operation.identities import contract_graph_identity, effective_context_identity
