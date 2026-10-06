# Boundary feedback follow-up

- [ ] Add native compact lifecycle output for `boundary authorize` and `boundary verify`.
  - Add an explicit CLI presentation option such as `--summary`; keep the existing full JSON output as the default for compatibility.
  - Define one documented stable summary envelope for both success and blocked results. It should expose the lifecycle stage/outcome, operation ID when available, change ID when available, selected task IDs, and diagnostics.
  - Emit an explicit empty diagnostics array on successful results rather than an ambiguous `null`/missing value.
  - Do not expose `gitBaseline`, dirty-path fingerprints, verification final-state fingerprints, or other full operation evidence in summary output.
  - Preserve the Boundary command's native exit status. A blocked authorize/verify must remain nonzero without requiring a shell pipeline or `pipefail`.
  - Summary mode limits stdout presentation only. Do not describe it as diagnostic redaction or a privacy boundary; stderr and stored operation evidence retain their normal semantics.
  - Keep authorization, verification, operation persistence, and the existing `boundary status` handoff semantics unchanged.
  - Update focused lifecycle/adapter documentation and add focused CLI/adapter tests before closing this item.

- [ ] Detect operation-evidence persistence problems before expensive lifecycle work.
  - Add a narrowly scoped readiness check for the actual current-worktree Git metadata location used by Boundary operation evidence.
  - The check must not overwrite, relocate, weaken, or silently bypass `current.json` or immutable archives.
  - Prefer a temporary create/remove probe in the intended Boundary metadata directory, with cleanup on both success and failure.
  - Run the check early enough that a sandbox or permissions problem is reported before contract resolution, baseline capture, or verification work that would otherwise need to be repeated.
  - Give persistence-readiness failure a stable machine-readable diagnostic/category rather than relying only on raw `OSError` text.
  - Document the required writable Git-metadata location and clarify that mise cache warnings are separate from Boundary evidence persistence.

- [ ] Document the Spec Kit follow-up-work recipe without weakening unique task write ownership.
  - Preserve the rule that one implementation path is declared by only one task in the active change.
  - Document that follow-up work on an already-owned path should refine/reopen the owning task outside an active implementation operation rather than append a duplicate convergence task.
  - Require fresh explicit task selection and authorization after that refinement.
  - Keep operation verification distinct from feature completion or live acceptance; a verified Boundary operation proves scope compliance, not feature correctness.
  - Prefer integration/task-generation guidance over a new Boundary core authority mechanism unless a concrete host limitation demonstrates that refinement cannot represent the work.

- [ ] Eliminate stale downstream instruction references to Boundary-owned lock files.
  - Audit canonical Spec Kit integration/materialization sources for generated instructions that can still mention `boundary.lock.json`.
  - Update the canonical generator/template rather than treating generated `.specify/` material as authoritative source.
  - Verify a fresh integration materialization contains only the mise-managed installation/version-selection model.
  - Do not hand-edit downstream generated state as the product fix.

Resolved feedback that should not be re-opened without new evidence:
- The `selectedTaskIds must be an array` failure was fixed in Boundary 0.1.4.
- Duplicate write declarations across Spec Kit tasks remain intentionally invalid; the improvement is workflow representation/guidance, not relaxed ownership.
