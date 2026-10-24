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

Expose the generic operation lifecycle, contract queries, status, and Boundary-owned agent integration.

## Invariants

- `pre-change` accepts only the versioned normalized request; `post-change` and `post-abandon` use stored evidence.
- Contract evolution uses `contracts pre-change` and the same closing commands.
- Lifecycle results have stable versioned stage, status, and diagnostic fields.
- Status, inspection, contract checking, and integration checking are read-only.
- Integration install and remove manage only Boundary skills and a root ignore block, and refuse open operations.

## Prohibitions

- No command reads or depends on a particular planning system's files.
- Old lifecycle command aliases are absent.
