---
schema: boundary.contract/v1
id: boundary-pre-change
owns:
  - src/boundary/operation/**
  - src/boundary/pre_change/**
depends_on:
  - boundary-context
  - boundary-native-contracts
  - boundary-repository
---

# Pre-change and Operation Evidence

## Purpose

Resolve exact selected scope and capture worktree state before edits.

## Invariants

- A fresh generic request, native contract graph, and Git snapshot determine one immutable operation record.
- Selection is explicit; task prose, unrelated tasks, and architectural ownership cannot enlarge scope.
- An open operation cannot be replaced.
- Dirty targets require exact verified predecessor output from the same change, kind, and selected task identity.
- Evidence is atomic and confined to `.boundary-state/` in the current worktree.
- The root managed ignore block must be installed before opening an operation.

## Prohibitions

- Boundary must not write evidence or exclusion rules under `.git/**`.
- An abandoned or modified predecessor output must not be carried forward.
- Mutable planning state must not rewrite historical operation scope.

## Interfaces

- Pre-change services open implementation or contract-evolution operations.
- Operation storage and status queries preserve current worktree evidence without cross-worktree coordination.
