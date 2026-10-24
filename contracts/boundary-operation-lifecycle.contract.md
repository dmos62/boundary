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

# Operation Lifecycle

## Purpose

Keep pre-change, post-change, and post-abandon transitions consistent.

## Invariants

- One writer per worktree is assumed; read-only queries may overlap that writer.
- A pre-change baseline precedes edits, and an open operation blocks another pre-change.
- Verified predecessor output may carry forward only when exact state and task identity match.
- Abandonment preserves evidence of unverified closure and never implies a successful check.
- Status and evidence are local to the current worktree.

## Prohibitions

- The lifecycle must not infer permission from task state, a clean Git status, or another worktree's operation.
- Failure to store a successor must not erase the prior valid record.
