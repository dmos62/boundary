# Boundary feedback follow-up

- [ ] Finish automatic operation-evidence persistence readiness at lifecycle entry.
  - Core operation storage now has a temporary create/remove probe against the actual current-worktree Git metadata directory.
  - Authorization invokes the probe before contract resolution or Git baseline capture.
  - Persistence failures use `OPERATION_EVIDENCE_UNAVAILABLE`, classified as `missing-external-prerequisite`; storage I/O failures use the same code.
  - Remaining: invoke the same core probe at native verification entry before operation verification work, and add focused verification-order coverage.
  - Remaining: document that the current-worktree Git metadata location used for `<git-dir>/boundary` must be writable while keeping the check automatic and out of the routine user-visible lifecycle.
  - Do not overwrite, relocate, weaken, or silently bypass `current.json` or immutable archives.
  - Keep unrelated mise cache warnings outside Boundary persistence semantics.
  - Run the full suite after verification wiring and resolve the currently exposed `boundary status --help` wrapping regression.

- [ ] Clarify the Spec Kit follow-up-work recipe without weakening unique task write ownership.
  - Preserve the rule that one implementation path is declared by only one task in the active change.
  - Document that follow-up work on an already-owned path should refine or reopen the owning task outside an active implementation operation rather than append a duplicate convergence task.
  - Require fresh explicit task selection and authorization after that refinement.
  - Keep operation verification distinct from feature completion or live acceptance; a verified Boundary operation proves scope compliance, not feature correctness.
  - Review current Spec Kit task-generation/refinement integration before deciding whether documentation alone is enough. If the host workflow makes reopening/refinement hard to discover, propose the smallest adapter-side guidance needed rather than adding new Boundary authority semantics.

- [ ] Eliminate stale downstream instruction references to Boundary-owned lock files.
  - Audit canonical Spec Kit integration/materialization sources for generated instructions that can still mention `boundary.lock.json`.
  - Update the canonical generator/template rather than treating generated `.specify/` material as authoritative source.
  - Verify a fresh integration materialization contains only the mise-managed installation/version-selection model.
  - Do not hand-edit downstream generated state as the product fix.

Resolved feedback that should not be re-opened without new evidence:
- The `selectedTaskIds must be an array` failure was fixed in Boundary 0.1.4.
- Duplicate write declarations across Spec Kit tasks remain intentionally invalid; the improvement is workflow representation/guidance, not relaxed ownership.
