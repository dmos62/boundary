"""CLI operations for canonical native contracts."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from boundary.authorization import (
    AuthorizationError,
    ContractEvolutionWriteSet,
    WriteSetError,
    authorize_contract_evolution_operation,
    read_current_operation,
)
from boundary.contracts import load_contract_graph
from boundary.outcomes import (
    LifecycleDiagnostic,
    LifecycleOutcome,
    LifecycleSuccess,
    classify_lifecycle_codes,
)


def configure_contracts_parser(
    parser: argparse.ArgumentParser,
) -> None:
    """Configure native-contract maintenance and evolution subcommands."""

    commands = parser.add_subparsers(
        dest="contracts_command",
        required=True,
    )
    commands.add_parser(
        "check",
        help="Validate canonical native contracts.",
        description="Validate canonical native contracts.",
    )

    authorize = commands.add_parser(
        "authorize",
        help="Authorize a separate persistent-contract evolution operation.",
        description=(
            "Authorize exact native contract targets for one isolated "
            "contract-evolution operation. Close it with boundary verify before "
            "authorizing dependent implementation."
        ),
    )
    authorize.add_argument(
        "--change",
        dest="change_id",
        required=True,
        metavar="CHANGE_ID",
        help=(
            "Change identity associated with this contract-evolution operation."
        ),
    )
    authorize.add_argument(
        "targets",
        nargs="+",
        metavar="CONTRACT",
        help=(
            "Exact repository-relative contracts/**/*.contract.md target "
            "authorized for evolution."
        ),
    )


def run_contracts_check(
    repository_root: Path,
    output: TextIO,
) -> int:
    """Validate canonical contracts and report a compact result."""

    graph = load_contract_graph(repository_root)
    count = len(graph.contracts)
    noun = "contract" if count == 1 else "contracts"
    print(
        f"contracts: ok ({count} {noun})",
        file=output,
    )
    return 0


def run_contracts_authorize(
    repository_root: Path,
    change_id: str,
    targets: Sequence[str],
    output: TextIO,
) -> int:
    """Authorize one isolated contract-evolution operation."""

    try:
        change = ContractEvolutionWriteSet(
            change_id=change_id,
            writes=tuple(targets),
        )
        record = authorize_contract_evolution_operation(
            repository_root,
            change,
        )
    except (AuthorizationError, WriteSetError) as exc:
        return _render_blocked_authorization(
            repository_root,
            change_id,
            exc,
            output,
        )

    result = LifecycleSuccess(
        stage="authorize",
        status="authorized",
        operation_id=record.operation_id,
        change_id=record.change_id,
        authorized_targets=tuple(
            target.path
            for target in record.authorized_targets
        ),
    )
    _print_document(result.to_document(), output)
    return 0


def _render_blocked_authorization(
    repository_root: Path,
    change_id: str,
    error: AuthorizationError | WriteSetError,
    output: TextIO,
) -> int:
    if isinstance(error, AuthorizationError):
        code = error.code or "BOUNDARY_FAILURE"
    else:
        code = "INVALID_WRITE_TARGET"

    classification = classify_lifecycle_codes(
        (code,),
        stage="authorize",
        operation_kind="contract-evolution",
    )
    operation_id = _active_operation_id(
        repository_root,
        code,
    )
    message = str(error)
    outcome = LifecycleOutcome(
        stage="authorize",
        category=classification.category,
        code=code,
        message=message,
        change_id=change_id,
        operation_id=operation_id,
        required_transition=classification.required_transition,
        diagnostics=(
            LifecycleDiagnostic(
                code=code,
                message=message,
            ),
        ),
    )
    _print_document(outcome.to_document(), output)
    return 2


def _active_operation_id(
    repository_root: Path,
    code: str,
) -> str | None:
    if code != "OPERATION_NOT_VERIFIED":
        return None
    try:
        current = read_current_operation(repository_root)
    except AuthorizationError:
        return None
    return None if current is None else current.operation_id


def _print_document(
    document: dict[str, object],
    output: TextIO,
) -> None:
    print(
        json.dumps(
            document,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        file=output,
    )
