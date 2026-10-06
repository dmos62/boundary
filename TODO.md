# Boundary feedback follow-up

- [ ] Finish the Spec Kit follow-up-work guidance in canonical integration material.
  - Core adapter semantics and Boundary scope/implementation procedure now preserve one-task-per-path ownership: follow-up work on an already-owned path refines or reopens the owning task outside an active implementation operation instead of appending a duplicate convergence task.
  - Fresh explicit selection and authorization are required after refinement; Boundary verification proves operation scope compliance only, not feature correctness, completion, or live acceptance.
  - The repository grep shows no follow-up/reopen guidance in `integration/speckit/` task-generation/refinement material.
  - The visible canonical integration tree has no preset or task-template source beside the adapter commands, extension manifest, workflow overlay, and runtime materializer. Inspect the runtime asset/materialization sources and repository-wide preset/template candidates next before choosing the canonical augmentation point.
  - Add the smallest discoverability guidance at that canonical source; do not add new Boundary authority semantics.

- [ ] Eliminate stale downstream instruction references to Boundary-owned lock files.
  - Audit canonical Spec Kit integration/materialization sources for generated instructions that can still mention `boundary.lock.json`.
  - Update the canonical generator/template rather than treating generated `.specify/` material as authoritative source.
  - Verify a fresh integration materialization contains only the mise-managed installation/version-selection model.
  - Do not hand-edit downstream generated state as the product fix.

Resolved feedback that should not be re-opened without new evidence:
- The `selectedTaskIds must be an array` failure was fixed in Boundary 0.1.4.
- Duplicate write declarations across Spec Kit tasks remain intentionally invalid; the improvement is workflow representation/guidance, not relaxed ownership.
