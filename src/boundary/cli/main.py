"""Provider-neutral Boundary command-line entry point."""

import argparse
from collections.abc import Sequence
from importlib.metadata import version as distribution_version
from pathlib import Path
import sys
from typing import TextIO

from boundary.pre_change.model import PreChangeError
from boundary.contracts import ContractGraphError, ContractParseError
from boundary.repository import RepositoryPathError
from .inspection import run_inspect, run_inspect_authorized
from .status import run_status
from .lifecycle import run_pre_change, run_contract_pre_change, run_post_change, run_post_abandon
from .integration import run_integration
from boundary.contracts import load_contract_graph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="boundary", description="Persistent contracts and exact worktree change scope.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {distribution_version('boundary-cli')}")
    commands = parser.add_subparsers(dest="command")
    inspect = commands.add_parser("inspect", help="Inspect effective contract context.")
    inspect.add_argument("--authorized", action="store_true", help="Inspect targets in the open operation.")
    inspect.add_argument("targets", nargs="*")
    pre = commands.add_parser("pre-change", help="Open an implementation operation from an explicit request.")
    pre.add_argument("--request", required=True, metavar="FILE", help="Versioned JSON request file, or - for stdin.")
    commands.add_parser("post-change", help="Check actual writes and close the open operation.")
    commands.add_parser("post-abandon", help="Close the open operation without verification.")
    commands.add_parser("status", help="Read the current worktree operation status.")
    contracts = commands.add_parser("contracts", help="Manage native contracts.")
    contract_commands = contracts.add_subparsers(dest="contracts_command", required=True)
    contract_commands.add_parser("check", help="Validate native contracts.")
    contract_pre = contract_commands.add_parser("pre-change", help="Open exact contract evolution.")
    contract_pre.add_argument("--change", required=True, dest="change_id")
    contract_pre.add_argument("targets", nargs="+", metavar="CONTRACT")
    integration = commands.add_parser("integration", help="Manage Boundary agent skills and state exclusion.")
    integration_commands = integration.add_subparsers(dest="integration_command", required=True)
    for action in ("install", "check", "remove"):
        integration_commands.add_parser(action)
    return parser


def main(argv: Sequence[str] | None = None, *, repository_root: str | Path | None = None, stdout: TextIO | None = None, stderr: TextIO | None = None, stdin: TextIO | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(repository_root) if repository_root is not None else Path.cwd()
    output = stdout if stdout is not None else sys.stdout
    errors = stderr if stderr is not None else sys.stderr
    source = stdin if stdin is not None else sys.stdin
    try:
        if args.command == "pre-change":
            return run_pre_change(root, args.request, source, output)
        if args.command == "post-change":
            return run_post_change(root, output)
        if args.command == "post-abandon":
            return run_post_abandon(root, output)
        if args.command == "status":
            return run_status(root, output)
        if args.command == "inspect":
            if args.authorized:
                if args.targets:
                    parser.error("--authorized cannot be combined with targets")
                return run_inspect_authorized(root, output, errors)
            if not args.targets:
                parser.error("inspect requires targets or --authorized")
            return run_inspect(root, args.targets, output)
        if args.command == "contracts":
            if args.contracts_command == "pre-change":
                return run_contract_pre_change(root, args.change_id, tuple(args.targets), output)
            graph = load_contract_graph(root)
            print(f"contracts: ok ({len(graph.contracts)} contracts)", file=output)
            return 0
        if args.command == "integration":
            return run_integration(root, args.integration_command, output)
    except (PreChangeError, ContractGraphError, ContractParseError, RepositoryPathError, OSError, ValueError) as exc:
        print(f"boundary: error: {exc}", file=errors)
        return 2
    parser.print_help(file=output)
    return 0
