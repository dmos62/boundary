"""CLI rendering for transient effective target context."""

from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from boundary.authorization import read_authorization_handoff
from boundary.contracts import ContractGraph, load_contract_graph
from boundary.context import (
    ProvenancedText,
    TargetContext,
    resolve_target_context,
)


def run_inspect(
    repository_root: Path,
    targets: Sequence[str],
    output: TextIO,
) -> int:
    """Resolve and render requested targets without persisting projections."""

    graph = load_contract_graph(repository_root)
    contexts = tuple(
        resolve_target_context(graph, target)
        for target in targets
    )
    print(_render_contexts(graph, contexts), file=output)
    return 0


def run_inspect_authorized(
    repository_root: Path,
    output: TextIO,
    errors: TextIO,
) -> int:
    """Render the current authorized unit with freshly resolved contexts."""

    handoff = read_authorization_handoff(repository_root)
    if handoff is None:
        return _authorized_error(
            errors,
            "no current Boundary operation is available",
        )
    if handoff.kind != "implementation":
        return _authorized_error(
            errors,
            "current Boundary operation is not an implementation operation",
        )
    if handoff.status != "authorized":
        return _authorized_error(
            errors,
            "current Boundary implementation operation is not authorized",
        )
    if not handoff.head_matches_baseline:
        return _authorized_error(
            errors,
            "current Git HEAD does not match the authorization baseline",
        )

    graph = load_contract_graph(repository_root)
    targets = tuple(
        target.path
        for target in handoff.authorized_targets
    )
    contexts = tuple(
        resolve_target_context(graph, target)
        for target in targets
    )
    selected = ", ".join(handoff.selected_task_ids) or "-"
    unit_lines = [
        "authorized-unit:",
        f"  operation-id: {handoff.operation_id}",
        f"  change-id: {handoff.change_id}",
        f"  kind: {handoff.kind}",
        f"  status: {handoff.status}",
        f"  selected-tasks: {selected}",
        "  targets:",
    ]
    unit_lines.extend(f"    - {target}" for target in targets)

    rendered = "\n\n".join(
        (
            "\n".join(unit_lines),
            _render_contexts(graph, contexts),
        )
    )
    print(rendered, file=output)
    return 0


def render_target_context(
    graph: ContractGraph,
    context: TargetContext,
) -> str:
    """Render one compact effective context with canonical provenance."""

    lines = [
        f"target: {context.target_path}",
        f"owner: {context.owner_id or '-'}",
        "applicable: "
        f"{', '.join(context.applicable_contract_ids) or '-'}",
    ]

    source_ids = set(context.applicable_contract_ids)
    source_ids.update(
        item.contract_id
        for item in context.dependency_interfaces
    )
    if source_ids:
        by_id = dict(graph.contracts_by_id)
        if not by_id:
            by_id = {
                contract.contract_id: contract
                for contract in graph.contracts
            }
        lines.append("sources:")
        for contract_id in sorted(source_ids):
            contract = by_id[contract_id]
            lines.append(
                f"  {contract_id}: {contract.source_path} "
                f"@ {contract.content_identity}"
            )

    _append_items(lines, "purpose", context.purposes)
    _append_items(lines, "invariants", context.invariants)
    _append_items(lines, "prohibitions", context.prohibitions)
    _append_items(lines, "interfaces", context.interfaces)
    _append_items(
        lines,
        "dependency-interfaces",
        context.dependency_interfaces,
    )
    return "\n".join(lines)


def _render_contexts(
    graph: ContractGraph,
    contexts: tuple[TargetContext, ...],
) -> str:
    return "\n\n".join(
        render_target_context(graph, context)
        for context in contexts
    )


def _authorized_error(
    errors: TextIO,
    message: str,
) -> int:
    print(f"boundary inspect --authorized: {message}", file=errors)
    return 2


def _append_items(
    lines: list[str],
    label: str,
    items: tuple[ProvenancedText, ...],
) -> None:
    if not items:
        return

    lines.append(f"{label}:")
    for item in items:
        text_lines = item.text.splitlines() or [""]
        lines.append(
            f"  - {item.contract_id}: {text_lines[0]}"
        )
        lines.extend(
            f"    {line}"
            for line in text_lines[1:]
        )
