---
schema: boundary.contract/v1
id: boundary-repository-tooling
owns:
  - scripts/**
  - pyproject.toml
  - mise.toml
  - .gitignore
  - AGENTS.md
  - files.include
  - dev-scripts.include
---

# Repository Tooling

## Purpose

Build, install, and validate the generic Boundary CLI through conventional project tooling.

## Invariants

- Mise selects and locks the Boundary Git source; Boundary maintains no second source or dependency lock.
- The installed `boundary` executable is the downstream command surface.
- Package assets include canonical, runtime-neutral Boundary skills but no planning-system or agent-runtime adapter.
- Root ignore management changes only the delimited Boundary block and keeps unrelated rules visible.

## Prohibitions

- Boundary must not install a pinned planning system or generate a copied runtime launcher.
- Distribution maintenance must not overwrite an open operation.
