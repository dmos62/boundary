---
schema: boundary.contract/v1
id: boundary-operation-lifecycle
applies_to:
  - src/boundary/operation/**
  - src/boundary/pre_change/**
  - src/boundary/post_change/**
depends_on:
  - boundary-pre-change
  - boundary-post-change
---

# Operation Evidence Lifecycle

## Purpose

Preserve the durable relationship between authorization evidence and Git-derived verification.

## Invariants

- Verification consumes the exact historical operation record created by authorization.
- A verified epoch may be replaced only through an explicit successor authorization.
- Carry-forward accepts only exact final states recorded by a verified predecessor.
- Operation evidence remains workflow history rather than canonical project semantics.
- Failure while constructing or installing successor evidence leaves the previous successful record usable.

## Prohibitions

- Verification must not reconstruct authority from current planning or task state.
- Successor authorization must not silently adopt unverified dirty target state.
