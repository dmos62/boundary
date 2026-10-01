"""Top-level Boundary command-line entry point."""

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys
from typing import TextIO

from boundary.authorization import AuthorizationError
from boundary.contracts import ContractGraphError, ContractParseError
from boundary.repository import RepositoryPathError

from .contracts import run_contracts_check
from .inspection import run_inspect
from .status import run_status


def build_parser() -> argparse.ArgumentParser:
    """Build the provider-neutral product command parser."""

    parser = argparse.ArgumentParser(
        prog="boundary",
        description="Persistent project contracts and operation authorization.",
    )
    commands = parser.add_subparsers(dest="command")

    contracts_parser = commands.add_parser(
        "contracts",
        help="Validate native project contracts.",
    )
    contract_commands = contracts_parser.add_subparsers(
        dest="contracts_command",
        required=True,
    )
    contract_commands.add_parser(
        "check",
        help="Validate canonical native contracts.",
    )

    inspect_parser = commands.add_parser(
        "inspect",
        help="Resolve effective contract context for repository targets.",
    )
    inspect_parser.add_argument(
        "targets",
        nargs="+",
        help="Repository-relative target path.",
    )

    authorize_parser = commands.add_parser(
        "authorize",
        help="Authorize one explicitly selected implementation unit.",
    )
    authorize_parser.add_argument(
        "--task",
        action="append",
        dest="task_ids",
        default=[],
        help="Select one implementation task; repeat for multi-task units.",
    )

    commands.add_parser(
        "verify",
        help="Verify actual writes against current authorization.",
    )
    commands.add_parser(
        "status",
        help="Show current Boundary authorization state.",
    )

    integration_parser = commands.add_parser(
        "integration",
        help="Manage Boundary-owned project integration.",
    )
    integration_commands = integration_parser.add_subparsers(
        dest="integration_command",
        required=True,
    )
    for action, help_text in (
        ("install", "Materialize Boundary-owned project integration."),
        ("check", "Validate Boundary-owned project integration."),
        ("remove", "Remove Boundary-owned project integration."),
    ):
        integration_commands.add_parser(action, help=help_text)

    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    repository_root: str | Path | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the Boundary CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)
    output = stdout if stdout is not None else sys.stdout
    errors = stderr if stderr is not None else sys.stderr
    root = (
        Path.cwd()
        if repository_root is None
        else Path(repository_root)
    )

    try:
        if args.command == "contracts":
            return run_contracts_check(root, output)
        if args.command == "inspect":
            return run_inspect(root, args.targets, output)
        if args.command == "status":
            return run_status(root, output)
        if args.command == "authorize":
            from boundary_host.commands import run_authorize

            return run_authorize(
                root,
                args.task_ids,
                output,
                errors,
            )
        if args.command == "verify":
            from boundary_host.commands import run_verify

            return run_verify(root, output, errors)
        if args.command == "integration":
            from boundary_host.integration import run_integration

            return run_integration(
                root,
                args.integration_command,
                output,
                errors,
            )
    except (
        AuthorizationError,
        ContractParseError,
        ContractGraphError,
        RepositoryPathError,
        OSError,
    ) as exc:
        print(f"boundary: error: {exc}", file=errors)
        return 2

    parser.print_help(file=output)
    return 0
