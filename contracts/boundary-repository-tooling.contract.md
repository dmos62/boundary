---
schema: boundary.contract/v1
id: boundary-repository-tooling
owns:
  - scripts/**
---

# Repository Tooling

## Purpose

Provide reproducible Boundary development tooling and downstream integration around a conventional mise-installed Boundary CLI.

## Invariants

- Downstream Boundary tool selection and exact source identity are managed through normal mise project configuration and lock state.
- The supported downstream distribution model installs Boundary from a stable Git source through mise.
- Locked installation preserves an exact Boundary Git source identity.
- Boundary does not require mise to freeze the complete transitive Python dependency graph for the Git-backed tool.
- Boundary package metadata defines compatible Python runtime dependencies.
- Boundary exposes one conventional installed `boundary` console entry point.
- Normal downstream Boundary commands do not require an operator-supplied Boundary checkout, Python import-path configuration, direct module invocation, or uv cache plumbing.
- Boundary-specific integration materialization is separate from mise-owned tool installation and version selection.
- Generated Boundary integration state remains recreatable from the installed Boundary CLI and is excluded locally rather than becoming canonical Boundary source.
- Host-owned persistent configuration and shareable generated state remain visible to Git rather than being hidden as Boundary-owned generated state.
- Pinned Spec Kit project-state ownership follows Spec Kit's managed `.specify/.gitignore`; Boundary does not patch or broaden that policy.
- The Spec Kit script mode selected by `.specify/init-options.json` is authoritative for execution.
- Inactive Spec Kit script variants retained by supported mode transitions are non-authoritative host-generated residue and are not deleted by Boundary.
- Installation and removal of host integration use supported host lifecycle mechanisms rather than patching generated state directly.
- Boundary source development uses repository mise tooling and remains distinct from downstream locked installation.
- Development bootstrap does not install or require the removed SpecDD migration provider.
- Integration failures identify missing prerequisites before relying on partially initialized generated state.

## Prohibitions

- Boundary must not define another project-local revision or dependency lock beside mise.
- Downstream portable state must not contain operator-local Boundary checkout paths.
- Boundary must not require source-checkout cleanliness or revision matching as a downstream lifecycle protocol.
- Boundary must not run a disposable package service merely to obtain a native Python dependency lock.
- Boundary must not hide raw uv or Python environment plumbing behind a nominally semantic downstream procedure.
- Generated integration state must not become canonical Boundary source.
- Boundary must not generate a project-local launcher solely to locate a copied Boundary runtime.
- Boundary must not broadly ignore `.specify/` or core `speckit-*` skills to suppress host-owned project-state changes.
- Boundary must not directly delete inactive Spec Kit script variants retained by the host lifecycle.
- Legacy `.specdd/` state must not be created as part of Boundary installation.

## Interfaces

- The installed `boundary` executable is the downstream semantic command surface.
- `boundary integration install` materializes or refreshes Boundary-owned host integration.
- `boundary integration check` validates Boundary-owned generated integration and required host prerequisites.
- `boundary integration remove` removes Boundary-owned generated integration without removing host-owned project state.
- Repository mise tasks provide source-development bootstrap, validation, and test entry points.
