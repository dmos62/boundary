"""Provider-neutral actual-write authorization checks."""

from pathlib import Path

from boundary.pre_change.engine import is_native_contract_path
from boundary.operation.identities import effective_context_identity
from boundary.operation.record import OperationRecord
from boundary.contracts import (
    ContractGraphError,
    ContractOwnershipError,
    ContractParseError,
    load_contract_graph,
)
from boundary.context import resolve_target_context

from .model import PostChangeDiagnostic


def check_allowed_writes(
    repository_root: str | Path,
    current: OperationRecord,
    paths: tuple[str, ...],
) -> list[PostChangeDiagnostic]:
    """Verify one operation kind without running feature convergence checks."""

    if current.kind == "implementation":
        return _check_implementation_writes(
            repository_root,
            current,
            paths,
        )
    return _check_contract_writes(current, paths)


def diagnostic(
    code: str,
    message: str,
    *paths: str,
) -> PostChangeDiagnostic:
    """Build one stable product-level diagnostic."""

    return PostChangeDiagnostic(
        code=code,
        message=message,
        paths=tuple(paths),
    )


def _check_implementation_writes(
    repository_root: str | Path,
    current: OperationRecord,
    paths: tuple[str, ...],
) -> list[PostChangeDiagnostic]:
    diagnostics: list[PostChangeDiagnostic] = []
    authorized = {
        target.path: target
        for target in current.allowed_targets
    }
    project_paths: list[str] = []
    for path in paths:
        if is_native_contract_path(path):
            diagnostics.append(
                diagnostic(
                    "OPERATION_KIND_VIOLATION",
                    f"implementation operation modified native contract: {path}",
                    path,
                )
            )
            continue
        project_paths.append(path)
        if path not in authorized:
            diagnostics.append(
                diagnostic(
                    "UNDECLARED_WRITE",
                    f"actual implementation write was not authorized: {path}",
                    path,
                )
            )

    if not project_paths:
        return diagnostics
    try:
        graph = load_contract_graph(repository_root)
    except ContractOwnershipError as exc:
        diagnostics.append(
            diagnostic("AMBIGUOUS_OWNERSHIP", str(exc), *project_paths)
        )
        return diagnostics
    except (ContractParseError, ContractGraphError) as exc:
        diagnostics.append(
            diagnostic("CONTRACT_GRAPH_INVALID", str(exc), *project_paths)
        )
        return diagnostics

    for path in project_paths:
        try:
            context = resolve_target_context(graph, path)
        except ContractOwnershipError as exc:
            diagnostics.append(
                diagnostic("AMBIGUOUS_OWNERSHIP", str(exc), path)
            )
            continue
        if context.owner_id is None:
            diagnostics.append(
                diagnostic(
                    "UNOWNED_WRITE_TARGET",
                    f"actual implementation write has no primary owner: {path}",
                    path,
                )
            )
            continue

        evidence = authorized.get(path)
        if evidence is None:
            continue
        identity = effective_context_identity(graph, context)
        if (
            evidence.owner != context.owner_id
            or evidence.effective_context_identity != identity
        ):
            diagnostics.append(
                diagnostic(
                    "CONTRACT_CONTEXT_CHANGED",
                    f"effective contract context changed after authorization: {path}",
                    path,
                )
            )
    return diagnostics


def _check_contract_writes(
    current: OperationRecord,
    paths: tuple[str, ...],
) -> list[PostChangeDiagnostic]:
    authorized = {
        target.path
        for target in current.allowed_targets
    }
    diagnostics: list[PostChangeDiagnostic] = []
    for path in paths:
        if not is_native_contract_path(path):
            diagnostics.append(
                diagnostic(
                    "OPERATION_KIND_VIOLATION",
                    f"contract-evolution operation modified project file: {path}",
                    path,
                )
            )
        elif path not in authorized:
            diagnostics.append(
                diagnostic(
                    "UNDECLARED_WRITE",
                    f"contract change was not authorized: {path}",
                    path,
                )
            )
    return diagnostics
