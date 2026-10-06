# Boundary feedback follow-up

- [ ] Simplify `boundary authorize` and `boundary verify` into concise lifecycle commands.
  - Backward compatibility with the current verbose command output is not a constraint. Prefer the clearest product API even when it changes the existing JSON shape.
  - Make concise lifecycle results the normal command output rather than adding an opt-in `--compact`/`--summary` compatibility mode.
  - Give authorize and verify one small, consistent machine-readable result shape centered on `status`, `stage`, operation/change identity when available, selected task IDs when applicable, and diagnostics.
  - Successful authorization should make the resulting implementation unit immediately understandable without dumping the persisted operation record. Include the exact authorized target paths when that materially avoids a follow-up query; do not expose baseline fingerprints or other storage-oriented evidence.
  - Successful verification should report that the operation closed successfully without dumping verification path-state fingerprints.
  - Blocked results should use the same obvious command-level shape rather than forcing callers to understand a substantially different success/error envelope.
  - Represent diagnostics consistently, including an explicit empty collection on success.
  - Preserve meaningful process exit status directly: success is zero and a blocked lifecycle transition is nonzero. No shell pipeline or `pipefail` workaround should be required.
  - Keep complete authorization and verification evidence in Boundary's operation store. The CLI result is a presentation/API projection, not the evidence record itself.
  - Keep `boundary status` focused on inspecting the current authorization handoff. Do not make users choose between multiple overlapping compact-output mechanisms.
  - Avoid adding output-format switches unless a concrete use case requires them. If detailed persisted evidence later needs a public inspection command, design that separately rather than retaining verbose authorize/verify output by default.
  - Update command help so the lifecycle and each command's output purpose are obvious from `boundary --help`, `boundary authorize --help`, and `boundary verify --help`.
  - Update focused lifecycle, authorization, and Spec Kit adapter documentation together with CLI/adapter tests.

- [ ] Detect operation-evidence persistence problems before expensive lifecycle work.
  - Add a narrowly scoped readiness check for the actual current-worktree Git metadata location used by Boundary operation evidence.
  - The check must not overwrite, relocate, weaken, or silently bypass `current.json` or immutable archives.
  - Prefer a temporary create/remove probe in the intended Boundary metadata directory, with cleanup on both success and failure.
  - Run the check early enough that a sandbox or permissions problem is reported before contract resolution, baseline capture, or verification work that would otherwise need to be repeated.
  - Give persistence-readiness failure a stable machine-readable diagnostic/category rather than relying only on raw `OSError` text.
  - Document the required writable Git-metadata location and clarify that mise cache warnings are separate from Boundary evidence persistence.

- [ ] Document the Spec Kit follow-up-work recipe without weakening unique task write ownership.
  - Preserve the rule that one implementation path is declared by only one task in the active change.
  - Document that follow-up work on an already-owned path should refine or reopen the owning task outside an active implementation operation rather than append a duplicate convergence task.
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
