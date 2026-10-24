---
schema: boundary.contract/v1
id: boundary-core
owns:
  - src/boundary/**
---

# Boundary Core

## Purpose

Provide native contracts, context, generic change requests, and deterministic worktree operation checks.

## Invariants

- Planning systems supply normalized task projections; Boundary owns scope and Git evidence.
- Native contracts and effective context remain independent of callers and agent runtimes.
- Current operation evidence is local, noncanonical workflow state.

## Prohibitions

- Core permission checks must not depend on provider file layouts, workflow stages, or agent prompt compliance.
- Boundary must not acquire a task tracker, cross-worktree lock, or external-service authority.
