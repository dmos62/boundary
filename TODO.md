# Boundary feedback follow-up

- [ ] Finish the Spec Kit follow-up-work guidance in canonical integration material.
  - Core adapter semantics and Boundary scope/implementation procedure now preserve one-task-per-path ownership: follow-up work on an already-owned path refines or reopens the owning task outside an active implementation operation instead of appending a duplicate convergence task.
  - Fresh explicit selection and authorization are required after refinement; Boundary verification proves operation scope compliance only, not feature correctness, completion, or live acceptance.
  - The repository grep shows no follow-up/reopen guidance in `integration/speckit/` task-generation/refinement material.
  - Repository-wide preset/template discovery found the canonical Spec Kit preset at `integration/speckit-preset/preset.yml` with its task-command augmentation at `integration/speckit-preset/commands/tasks.md`.
  - `host_install.py` materializes that preset through Spec Kit, while `host_check.py` compares the installed preset tree against the canonical assets and requires the resulting `speckit-tasks` skill to contain `## Boundary Write Scope`. This identifies `integration/speckit-preset/commands/tasks.md` as the canonical augmentation point.
  - Add the smallest discoverability guidance there: follow-up work on an already-owned path must refine or reopen the owning task outside an active implementation operation, then receive fresh explicit selection and authorization. Keep Boundary verification described only as write-scope compliance; do not add new Boundary authority semantics.

- [ ] Eliminate stale downstream instruction references to Boundary-owned lock files.
  - Audit canonical Spec Kit integration/materialization sources for generated instructions that can still mention `boundary.lock.json`.
  - Current repository grep finds no `boundary.lock.json` reference in canonical project sources outside the harness-only TODO and diagnostic script; fresh integration materialization still needs verification.
  - Update the canonical generator/template rather than treating generated `.specify/` material as authoritative source if fresh materialization exposes stale guidance.
  - Verify a fresh integration materialization contains only the mise-managed installation/version-selection model.
  - Do not hand-edit downstream generated state as the product fix.

Resolved feedback that should not be re-opened without new evidence:
- The `selectedTaskIds must be an array` failure was fixed in Boundary 0.1.4.
- Duplicate write declarations across Spec Kit tasks remain intentionally invalid; the improvement is workflow representation/guidance, not relaxed ownership.
