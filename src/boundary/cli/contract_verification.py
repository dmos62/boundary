"""CLI closure for authorized native contract-evolution operations."""

import json
from pathlib import Path
from typing import TextIO

from boundary.authorization import AuthorizationError, read_current_operation
from boundary.outcomes import LifecycleSuccess
from boundary.verification import VerificationError, finalize_operation_verification
from boundary_host.adapter import path_classifier
from boundary_host.outcomes import outcome_for_error


def run_contract_evolution_verify(
    repository_root: Path,
    output: TextIO,
    errors: TextIO,
) -> int:
    """Verify contract evolution with the Spec Kit bookkeeping classifier.

    The native verification service owns all write-scope, Git baseline,
    authorization-evidence, and finalization decisions. This entrypoint
    supplies only deterministic host-owned path classification.
    """
    del errors

    operation = read_current_operation(repository_root)
    if operation is None or operation.kind != "contract-evolution":
        raise AuthorizationError(
            "no contract-evolution operation is available for verification",
            code="OPERATION_CHANGED",
        )

    try:
        verified = finalize_operation_verification(
            repository_root,
            operation_id=operation.operation_id,
            classify_path=path_classifier(
                f"specs/{operation.change_id}"
            ),
        )
    except (VerificationError, AuthorizationError) as exc:
        outcome = outcome_for_error(
            "verify",
            exc,
            change_id=operation.change_id,
            operation_id=operation.operation_id,
        )
        _print_document(outcome.to_document(), output)
        return 2

    result = LifecycleSuccess(
        stage="verify",
        status="verified",
        operation_id=verified.operation_id,
        change_id=verified.change_id,
    )
    _print_document(result.to_document(), output)
    return 0


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
