# Boundary feedback follow-up

- [ ] Redesign the routine CLI path around the smallest clear Boundary workflow.
  - Treat the intended direct-use happy path as:
    1. `boundary authorize T012 [T013 ...]`
    2. `boundary inspect --authorized`
    3. implement and run ordinary project checks
    4. `boundary verify`
  - In integrations where authorize/verify are lifecycle gates, the implementation worker should normally need only `boundary inspect --authorized` before editing.
  - Replace repeated `--task` flags with positional task IDs for direct CLI use. Explicit selection remains mandatory; positional syntax is still explicit authority input.
  - Keep `BOUNDARY_TASK_IDS` only as adapter/workflow transport where a shell integration needs it. Do not make environment transport part of the ordinary human-facing CLI.
  - Make `boundary authorize` emit a concise result describing the authorized unit: status, operation ID, change ID, selected tasks, and exact authorized targets. Do not dump the persisted operation record, Git baseline fingerprints, or storage-oriented evidence.
  - Make `boundary verify` emit a similarly concise result: status, operation ID, change ID, selected tasks when useful, and diagnostics. Do not dump verification path-state fingerprints.
  - Use one consistent command-result vocabulary for successful and blocked authorize/verify results. Successful results should contain an explicit empty diagnostics collection.
  - Preserve useful nonzero process exit status for blocked lifecycle transitions without requiring wrappers or pipelines.
  - Add `boundary inspect --authorized` as a read-only convenience over the current authorized operation:
    - require a current `implementation` operation with `status: authorized`;
    - require current HEAD to match its authorization baseline;
    - inspect the exact authorized target set from historical operation evidence rather than current mutable tasks;
    - resolve fresh effective Boundary context for those targets;
    - render the authorized-unit identity plus the target contexts in one invocation;
    - grant no new authority and create no lifecycle state.
  - Keep ordinary `boundary inspect <target...>` for planning, undeclared-target investigation, and focused queries.
  - Keep `boundary status` as a recovery/handoff/debugging query, not a required happy-path command before implementation when `inspect --authorized` has already established current operation identity, baseline freshness, targets, and effective context.
  - Update the implementation skill accordingly so it does not require both `status` and separate per-target inspection during routine use.
  - Make `boundary --help` lead with the routine lifecycle and distinguish routine commands from situational queries and maintenance commands.
  - Keep the core product vocabulary small: `authorize`, `inspect`, `verify`, `status`, `contracts`, and `integration`. Do not add aliases or output-mode switches without a concrete need.
  - Before implementation, inspect the focused CLI/adapter tests and integration call sites and re-include only those relevant tests in `files.include`. Confirm that positional direct selection and environment-based workflow transport can remain separate without special-case ambiguity.
  - Reconsider, but do not automatically add, a compound `boundary next <task...>` command. Only add it if actual multi-unit direct usage demonstrates that explicit `verify` followed by `authorize` is recurring friction worth the extra API surface and partial-success semantics.
  - Update `docs/spec-authorization.md`, `docs/spec-change-adapter.md`, `docs/spec-lifecycle.md`, focused CLI help, Spec Kit integration instructions, and tests together.

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
