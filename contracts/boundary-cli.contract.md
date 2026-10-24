---
schema: boundary.contract/v1
id: boundary-cli
owns:
  - src/boundary/cli/**
  - src/boundary/__main__.py
depends_on:
  - boundary-context
  - boundary-native-contracts
---

# Boundary CLI

## Purpose

Expose the generic operation lifecycle, contract queries, status, worktree-state setup, and optional skill delivery.

## Invariants

- `pre-change` accepts only the versioned normalized request; `post-change` and `post-abandon` use stored evidence.
- Contract evolution uses `contracts pre-change` and the same closing commands.
- Lifecycle results have stable versioned stage, status, and diagnostic fields.
- Status, inspection, contract checking, state checking, and skill checking are read-only.
- State setup manages only Boundary's local-evidence ignore rule and refuses an open operation.
- Optional skill delivery requires an explicit caller-selected directory and has no agent-specific default.

## Prohibitions

- No command reads or depends on a particular planning system's files.
- No command selects an agent runtime or writes into a runtime-specific directory by default.
- Old lifecycle command aliases are absent.
