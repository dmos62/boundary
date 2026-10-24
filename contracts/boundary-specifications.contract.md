---
schema: boundary.contract/v1
id: boundary-specifications
owns:
  - docs/spec.md
  - docs/spec-architecture.md
  - docs/spec-contracts.md
  - docs/spec-agent-instructions.md
  - docs/spec-request.md
  - docs/spec-pre-change.md
  - docs/spec-post-change.md
  - docs/spec-lifecycle.md
  - docs/spec-distribution.md
  - docs/spec-distribution-state.md
---

# Boundary Specifications

## Purpose

Define current Boundary behavior by native contract, request, operation, and distribution responsibilities.

## Invariants

- Current specifications describe the generic CLI and worktree-local lifecycle.
- Historical provider behavior remains historical and has no compatibility authority.
- Focused documents own detailed semantics without duplicating a migration checklist.
