"""Fresh canonical authorization for native Boundary operations."""

from pathlib import Path

from boundary.context import resolve_target_context
from boundary.contracts import (
    ContractGraph,
    ContractGraphError,
    ContractOwnershipError,
    ContractParseError,
    load_contract_graph,
)

from boundary.operation.identities import contract_graph_identity, effective_context_identity
from .model import (
    PreChangeError,
    ResolvedTarget,
    ChangeWriteSet,
    ContractScope,
    ContractEvolutionWriteSet,
    ImplementationScope,
)


def resolve_implementation_scope(
    repository_root: str | Path,
    change: ChangeWriteSet,
    *,
    selected_task_ids: tuple[str, ...] | None = None,
) -> ImplementationScope:
    """Authorize one explicit implementation unit against a fresh graph."""

    selected_tasks = change.select_tasks(selected_task_ids)
    selected_ids = tuple(
        task.task_id
        for task in selected_tasks
        if task.task_id is not None
    )
    writes = tuple(
        write
        for task in selected_tasks
        for write in task.writes
    )

    graph = _load_graph(repository_root)
    targets: list[ResolvedTarget] = []
    for path in writes:
        if is_native_contract_path(path):
            raise PreChangeError(
                "OPERATION_KIND_VIOLATION: implementation operations may "
                f"not modify native contracts: {path}",
                code="OPERATION_KIND_VIOLATION",
            )
        try:
            context = resolve_target_context(graph, path)
        except ContractOwnershipError as exc:
            raise PreChangeError(
                "AMBIGUOUS_OWNERSHIP: implementation write has ambiguous "
                f"ownership: {path}",
                code="AMBIGUOUS_OWNERSHIP",
            ) from exc
        if context.owner_id is None:
            raise PreChangeError(
                "UNOWNED_WRITE_TARGET: implementation write has no primary "
                f"owner: {path}",
                code="UNOWNED_WRITE_TARGET",
            )
        targets.append(
            ResolvedTarget(
                path=path,
                owner_id=context.owner_id,
                effective_context_identity=effective_context_identity(
                    graph,
                    context,
                ),
            )
        )

    return ImplementationScope(
        change_id=change.change_id,
        selected_task_ids=selected_ids,
        tasks=selected_tasks,
        targets=tuple(targets),
        contract_graph_identity=contract_graph_identity(graph),
    )


def resolve_contract_scope(
    repository_root: str | Path,
    change: ContractEvolutionWriteSet,
) -> ContractScope:
    """Authorize exact native-contract writes separately from implementation."""

    if not change.writes:
        raise PreChangeError(
            "contract-evolution authorization requires at least one target"
        )
    for path in change.writes:
        if not is_native_contract_path(path):
            raise PreChangeError(
                "OPERATION_KIND_VIOLATION: contract-evolution operations may "
                f"modify only native contracts: {path}",
                code="OPERATION_KIND_VIOLATION",
            )

    graph = _load_graph(repository_root)
    return ContractScope(
        change_id=change.change_id,
        targets=change.writes,
        contract_graph_identity=contract_graph_identity(graph),
    )


def is_native_contract_path(path: str) -> bool:
    """Return whether a canonical path names a native Boundary contract."""

    return (
        path.startswith("contracts/")
        and path.endswith(".contract.md")
    )


def _load_graph(repository_root: str | Path) -> ContractGraph:
    try:
        return load_contract_graph(repository_root)
    except ContractOwnershipError as exc:
        raise PreChangeError(
            f"AMBIGUOUS_OWNERSHIP: {exc}",
            code="AMBIGUOUS_OWNERSHIP",
        ) from exc
    except (ContractParseError, ContractGraphError) as exc:
        raise PreChangeError(
            f"CONTRACT_GRAPH_INVALID: {exc}",
            code="CONTRACT_GRAPH_INVALID",
        ) from exc
