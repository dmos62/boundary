"""Top-level Boundary command-line entry point."""

import argparse
from collections.abc import Sequence
from importlib.metadata import version as distribution_version
from pathlib import Path
import sys
from typing import TextIO

from boundary.authorization import AuthorizationError
from boundary.contracts import ContractGraphError, ContractParseError
from boundary.repository import RepositoryPathError

from .contracts import (
    configure_contracts_parser,
    run_contracts_authorize,
    run_contracts_check,
)
from .inspection import run_inspect, run_inspect_authorized
from .status import run_status


def build_parser() -> argparse.ArgumentParser:
    """Build the provider-neutral product command parser."""

    parser = argparse.ArgumentParser(
        prog="boundary",
        description=(
            "Persistent project contracts and operation authorization for "
            "coding agents.\nAuthorize an explicit task-selected unit, inspect "
            "its effective context, implement it, then verify actual writes."
        ),
        epilog=(
            "Routine implementation lifecycle:\n"
            "  boundary authorize T012 [T013 ...]\n"
            "  boundary inspect --authorized\n"
            "  implement only the authorized targets and run project checks\n"
            "  boundary verify\n"
            "\n"
            "Persistent-contract evolution:\n"
            "  boundary contracts authorize --change CHANGE_ID CONTRACT [...]\n"
            "  modify only the authorized contract targets\n"
            "  boundary contracts check\n"
            "  boundary verify\n"
            "  authorize dependent implementation only after closure\n"
            "\n"
            "Situational queries:\n"
            "  boundary inspect <target...>\n"
            "  boundary status\n"
            "\n"
            "Maintenance:\n"
            "  boundary contracts check\n"
            "  boundary integration install|check|remove"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {distribution_version('boundary-cli')}",
        help="Show the installed Boundary distribution version and exit.",
    )
    commands = parser.add_subparsers(dest="command")

    inspect_parser = commands.add_parser(
        "inspect",
        help="Inspect effective context for targets or the authorized unit.",
        description=(
            "Resolve effective Boundary contract context without persisting "
            "state. Pass repository targets for focused inspection, or use "
            "--authorized to inspect the exact current authorized target set."
        ),
    )
    inspect_parser.add_argument(
        "--authorized",
        action="store_true",
        help=(
            "Inspect the exact targets from the current authorized "
            "implementation operation and require a fresh Git baseline."
        ),
    )
    inspect_parser.add_argument(
        "targets",
        nargs="*",
        help="Repository-relative target path for focused inspection.",
    )

    authorize_parser = commands.add_parser(
        "authorize",
        help="Authorize one explicitly selected implementation unit.",
        description=(
            "Authorize one implementation unit from explicitly selected tasks "
            "in the active change. For direct use, pass one or more task IDs "
            "positionally. Workflow integrations may use adapter transport."
        ),
    )
    authorize_parser.add_argument(
        "task_ids",
        nargs="*",
        metavar="TASK_ID",
        help=(
            "Task ID selected for this implementation unit. Pass multiple "
            "IDs for a multi-task unit."
        ),
    )

    commands.add_parser(
        "verify",
        help="Verify actual writes against current authorization.",
        description=(
            "Verify actual Git changes against the current historical "
            "authorization and close the operation on success."
        ),
    )
    commands.add_parser(
        "status",
        help="Show current Boundary authorization state.",
        description=(
            "Emit the current Boundary authorization handoff as JSON, or null "
            "when no current operation exists. Intended for recovery, handoff, "
            "and debugging rather than the routine implementation path."
        ),
    )

    contracts_parser = commands.add_parser(
        "contracts",
        help="Authorize evolution or validate native project contracts.",
        description=(
            "Authorize isolated persistent-contract evolution or validate "
            "canonical native project contracts."
        ),
    )
    configure_contracts_parser(contracts_parser)

    integration_parser = commands.add_parser(
        "integration",
        help="Manage Boundary-owned project integration.",
        description=(
            "Manage Boundary-owned generated project integration separately "
            "from mise-owned Boundary installation and version selection."
        ),
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
        integration_commands.add_parser(
            action,
            help=help_text,
            description=help_text,
        )

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
            if args.contracts_command == "check":
                return run_contracts_check(root, output)
            return run_contracts_authorize(
                root,
                args.change_id,
                args.targets,
                output,
            )
        if args.command == "inspect":
            if args.authorized:
                if args.targets:
                    print(
                        "boundary: error: --authorized cannot be combined "
                        "with explicit targets",
                        file=errors,
                    )
                    return 2
                return run_inspect_authorized(root, output, errors)
            if not args.targets:
                print(
                    "boundary: error: inspect requires one or more targets "
                    "or --authorized",
                    file=errors,
                )
                return 2
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
