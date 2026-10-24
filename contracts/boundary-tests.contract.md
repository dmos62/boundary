---
schema: boundary.contract/v1
id: boundary-tests
owns:
  - tests/**
---

# Boundary Tests

## Purpose

Exercise contracts, generic requests, worktree state, lifecycle results, integration ownership, and installed distribution.

## Invariants

- Tests cover exact scope, changed `HEAD`, abandonment, dirty-target provenance, and independent worktrees.
- Installed CLI tests require no planning-system runtime.
- Legacy evidence is rejected rather than imported.
- Repository contract tests verify ownership and additive applicability.
