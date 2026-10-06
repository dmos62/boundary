# Boundary feedback follow-up

- [ ] Finish validating the routine CLI workflow redesign.
  - Production and canonical instruction changes now target the direct happy path:
    1. `boundary authorize T012 [T013 ...]`
    2. `boundary inspect --authorized`
    3. implement and run ordinary project checks
    4. `boundary verify`
  - Direct task selection is positional. `BOUNDARY_TASK_IDS` remains adapter/workflow transport used only when no positional selection is supplied.
  - Authorize and verify now target one concise `boundary.lifecycle-result/v1` vocabulary with explicit empty diagnostics on success and nonzero exit status for blocked transitions.
  - `boundary inspect --authorized` is designed to require a current authorized implementation operation and matching authorization `HEAD`, use historical authorized targets, and fresh-resolve target context without creating authority.
  - `boundary status` remains a recovery/handoff/debugging query instead of a routine implementation prerequisite.
  - No compound `boundary next` command was added; there is still no usage evidence justifying the extra API and partial-success semantics.
  - Before closing this item, inspect and update the focused CLI/adapter tests reintroduced by `files.include`, confirm direct positional selection remains separate from environment workflow transport, run the full checks, and narrow the test include set again.

- [ ] Detect operation-evidence persistence problems automatically before expensive lifecycle work.
  - This must not add another user-visible readiness step to the routine workflow.
  - Probe the actual current-worktree Git metadata location used for Boundary operation evidence internally at authorize/verify entry.
  - Do not overwrite, relocate, weaken, or silently bypass `current.json` or immutable archives.
  - Prefer a temporary create/remove probe in the intended Boundary metadata directory, with cleanup on both success and failure.
  - Fail before contract resolution, Git baseline work, or verification work that would otherwise need to be repeated when persistence is unavailable.
  - Give persistence-readiness failure a stable machine-readable diagnostic/category rather than relying only on raw `OSError` text.
  - Document the required writable Git-metadata location while keeping the check automatic.
  - Keep unrelated mise cache warnings outside Boundary persistence semantics.

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
