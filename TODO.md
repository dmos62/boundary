# Boundary feedback follow-up

- [ ] Eliminate stale downstream instruction references to Boundary-owned lock files.
  - Audit canonical Spec Kit integration/materialization sources for generated instructions that can still mention `boundary.lock.json`.
  - Current repository grep finds no `boundary.lock.json` reference in canonical project sources outside the harness-only TODO and diagnostic script; fresh integration materialization still needs verification.
  - Update the canonical generator/template rather than treating generated `.specify/` material as authoritative source if fresh materialization exposes stale guidance.
  - Verify a fresh integration materialization contains only the mise-managed installation/version-selection model.
  - Do not hand-edit downstream generated state as the product fix.

Resolved feedback that should not be re-opened without new evidence:
- The `selectedTaskIds must be an array` failure was fixed in Boundary 0.1.4.
- Duplicate write declarations across Spec Kit tasks remain intentionally invalid; the improvement is workflow representation/guidance, not relaxed ownership.
