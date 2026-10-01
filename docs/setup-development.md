# Boundary Development Setup

This guide is for contributors working on Boundary source itself.

Downstream project installation is documented separately in [setup-downstream.md](setup-downstream.md).

## Development model

Boundary source development uses mise as the repository tool-environment entry point.

The repository `mise.toml` selects the development Python and uv tools, pins the supported Spec Kit CLI, activates the project virtual environment, and exposes repository tasks.

Contributors should not need to reconstruct Python import paths, direct uv commands, copied runtime locations, or source-checkout consumer commands for normal development.

The development environment exposes the same installed `boundary` console command used by downstream projects.

## Bootstrap the source repository

Install the repository tools and run the bootstrap task:

    mise install
    mise run bootstrap

The bootstrap task installs the current checkout into the mise-managed development environment, materializes Boundary-owned Spec Kit/Codex integration through the installed CLI, and checks that integration.

Codex must already be available on `PATH`.

For a project that is not yet initialized with Spec Kit, Boundary lets pinned Spec Kit choose its platform-default script mode.

For an existing Spec Kit setup, Boundary preserves the selected script mode unless the contributor deliberately requests a transition.

Set:

    BOUNDARY_SPECKIT_SCRIPT=sh|ps|py mise run bootstrap

only when intentionally changing that mode through the supported Spec Kit lifecycle.

An explicit `ps` selection requires `pwsh` on `PATH`.

## Boundary CLI during development

Normal development uses the installed semantic CLI.

Examples:

    boundary contracts check
    boundary inspect <target...>
    boundary status
    boundary integration check

Repository mise tasks provide repeatable project-wide entry points.

Contributors should not need Python import-path configuration, module-level CLI invocation, direct uv environment plumbing, or generated project-local launchers for routine work.

## Core checks

Use:

    mise run contracts-check
    mise run test

Additional focused tasks may separate native core, Spec Kit adapter, and distribution tests when that improves iteration speed.

Those tasks are repository-development conveniences rather than downstream product APIs.

## Local source development

The local Boundary checkout is authoritative for editing Boundary itself.

The `dev-install` mise task installs that checkout into the repository's mise-managed development environment, using editable installation as a development convenience.

That local-source workflow is not a downstream source-distribution protocol and its filesystem path is not portable project state.

## Spec Kit script mode

Boundary development integration respects the script mode selected in `.specify/init-options.json`.

A project selecting `"script": "ps"` requires PowerShell.

A project selecting `"script": "sh"` requires Bash.

A project selecting `"script": "py"` uses the Python interpreter available to the installed Boundary integration.

An intentional script-mode transition goes through Spec Kit's supported lifecycle rather than direct edits to generated scripts.

Inactive script variants retained by Spec Kit after a transition remain non-authoritative host-generated residue.

## Source and generated state

Canonical Boundary source includes `src/boundary/`, package metadata, canonical skills, concrete adapters, integration source, contracts, and documentation.

The installed package also carries the canonical integration assets needed by `boundary integration ...`; those packaged copies are build artifacts, not a second source of project semantics.

Generated `.specify/` installation state and materialized agent skills are not replacements for canonical source.

Repository mise configuration and tasks define development tooling.

Downstream projects separately select Boundary through their own Git-backed mise configuration and lock state.

The development checkout therefore has no Boundary-specific consumer lock, source-checkout matching protocol, copied Boundary runtime, or generated project-local launcher.
