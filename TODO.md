# Boundary feedback follow-up review

Goal: perform a source-backed follow-up to `BOUNDARY-FEEDBACK-REVIEW1.md` against the current Boundary architecture and implementation, and determine which concerns were answered, clarified, intentionally rejected/superseded, only documented, fully implemented, or remain open.

The review must not treat documentation promises as implementation evidence. For each concern, distinguish:

- current specified semantics;
- concrete implementation behavior;
- automated-test evidence;
- integration/runtime evidence where applicable;
- whether the original concern is now addressed, partially addressed, intentionally out of scope, or unresolved.

Use the 2026-09-28 review as historical evidence only. Current `docs/spec*.md`, native contracts, source, and current tests define present Boundary behavior.

## Evidence carried forward from the completed implementation-unit review

Current specification and the supported authorization path agree on the implementation-unit model:

- one implementation unit is an explicit non-empty selection of task identities from the active change;
- selected tasks are normalized into canonical host order;
- the authorized write set is exactly the deterministic ordered union of those selected tasks' structured writes;
- omitted selection never means all feature tasks;
- one feature may proceed through multiple separately authorized operation epochs;
- a selected unit may span multiple architectural owners;
- ownership is resolved independently for every target and recorded in operation evidence;
- ownership supplies context and constraints but does not infer unit membership or widen task selection.

Scope discovery never widens the active operation. A path declared by an unselected task requires closure of the current operation and fresh authorization selecting the relevant next task set. An undeclared path additionally requires structured task-scope refinement before fresh authorization. Same-owner and cross-owner discoveries currently have the same authority consequence; the product specifications permit different coordination diagnostics but do not require different permissions. Persistent-contract evolution remains a separate operation kind and dependent implementation requires fresh authorization afterward.

The T012 / `clipboard.rs` regression is answered directly by current semantics: selecting only T012-like task scope would authorize only T012's declared writes. A `clipboard.rs` path declared only by T009 would remain unauthorized even when both tasks resolve to the same architectural owner. Writing it would be an `UNDECLARED_WRITE` at verification. The supported transition is to verify and close the current unit, then fresh-authorize a unit explicitly selecting T009 or another task set that declares the path.

One implementation-integrity gap was found. Normal authorization constructs internally consistent records, but persisted-record decoding and `OperationRecord` validation do not currently prove that an implementation record's `authorizedTargets` exactly equal the selected tasks' write union, and do not require `owner` plus `effectiveContextIdentity` on implementation target evidence. A syntactically valid but internally inconsistent operation document can therefore be loaded even though it could not be produced by the supported authorization path. Track this as a concrete follow-up rather than treating normal-path construction as proof that persisted authority is self-validating.

## Evidence carried forward from the active-worker authority review

Current specification, source, and focused tests agree that the active `OperationRecord` is the authority-bearing historical evidence for one epoch. Implementation records persist the explicit selected task identities and exact authorized target evidence; verification consumes that record rather than re-reading current task scope. The record model is frozen in memory, and verification closure preserves the authority fields while changing only lifecycle status and final-state evidence.

`boundary status` is a read-only projection of the current record plus a fresh Git `HEAD` read. Its `boundary.authorization-handoff/v1` document exposes operation/change identity, kind, lifecycle status, selected task identities, exact target evidence, contract-graph identity, authorization-time `HEAD`, current `HEAD`, and `headMatchesBaseline`. This is sufficient for a delegated worker to identify the current operation and write scope without rediscovering adapter scripts or runtime package paths. The handoff does not select tasks, widen authority, refresh contract context, or close an epoch.

Provider-neutral handoff fields keep stale, closed, and wrong-kind operations distinguishable: stale Git state is visible through `headMatchesBaseline`, closure through `status: verified`, and operation kind through `kind`. The Spec Kit verification path also blocks a feature mismatch with `OPERATION_CHANGED`. However, the concrete Spec Kit runtime currently has no implementation of the non-blocking adapter `status` query described in `docs/spec-change-adapter.md` that would pair the handoff with an active-feature match result. Treat that as current specification/implementation drift to resolve during the drift pass rather than as evidence that the authority model itself is unclear.

Machine-readable blocking outcomes are implemented through `boundary.lifecycle-outcome/v1`. Provider-neutral classification and the Spec Kit adapter distinguish invalid adapter state, missing external prerequisites, stale authorization, verification write-scope failures, scope-expansion transitions, and contract-evolution transitions without parsing diagnostic prose. Focused lifecycle-outcome tests cover invalid task selection, missing prerequisites, and unowned verification writes.

Review1's broader controller distinction is intentionally only partly a Boundary concern. Boundary classifies Boundary lifecycle failures and can identify required Boundary transitions, but it does not classify ordinary implementation/test failures or decide whether an outer controller should pause, retry, ask a human, or continue. `docs/spec-lifecycle.md` assigns those orchestration decisions to the higher-level controller.

## Evidence carried forward from the lifecycle/distribution ergonomics review

The mechanical-discovery concern from Review1 is addressed independently of the implementation-unit redesign.

The current package and CLI surface provide stable semantic entrypoints for all normal Boundary operations involved in the review:

- `boundary inspect <target...>` for effective-context inspection;
- `boundary authorize --task <task-id>` with repeated `--task` arguments for explicit implementation-unit authorization;
- `boundary verify` for operation verification;
- `boundary status` for the current authorization handoff;
- `boundary contracts check` for native-contract validation;
- `boundary integration install`, `check`, and `remove` for generated integration lifecycle.

This surface is concrete implementation rather than documentation-only intent. `pyproject.toml` exposes `boundary = "boundary.cli:main"` as the installed console script. The wheel contains the provider-neutral `boundary` package and the concrete `boundary_host` runtime, and force-includes canonical skills, runtime materializers, Spec Kit commands, extension metadata, workflow overlay, and preset assets.

Focused distribution coverage supplies runtime evidence. The mise Git-source integration test installs Boundary into mise-managed tool state, resolves the installed executable outside the consumer repository, invokes its command surface, installs/checks/removes generated integration, and confirms that no project-local `.boundary` runtime, `.specify/boundary-runtime`, or `boundary.lock.json` is required. The lock test separately verifies that `mise.lock` preserves exact Boundary Git source identity until an explicit mise lock bump. The current distribution-focused suite passes 9 tests, and the complete suite passes 101 tests.

Normal downstream use therefore no longer requires `PYTHONPATH`, direct `python -m boundary` invocation, caller-managed uv cache plumbing, locating `adapter_gate.py`, locating copied Boundary runtime source, a generated project-local Boundary launcher, or an operator-supplied Boundary checkout. The retained Python module entrypoints are compatibility/conventional package entrypoints rather than required downstream procedure. The `UV_CACHE_DIR` occurrence in the distribution test helper is isolated test-environment plumbing, not part of the consumer command contract.

The legacy-invocation search still finds retired invocation strings inside generated `.agents/` and `.specify/` material in the source checkout, plus negative assertions and normative text describing what must not be required. Project policy explicitly makes generated `.agents/` and `.specify/` material noncanonical; current behavior must be judged from `skills/`, `integration/`, packaged runtime source, and tests rather than those generated snapshots. The canonical integration assets and current workflow overlay invoke the installed `boundary` command directly.

The mechanical improvement should remain distinct in the final review from the implementation-unit improvement. Review1's feature-wide authorization problem was answered by task-selected authorization semantics. Its repeated command/path discovery problem was answered by conventional packaging, mise-managed installation, packaged integration assets, and one installed semantic CLI. Neither improvement depends on treating architectural ownership as implementation-unit membership.

No current README/specification correction was demonstrated by this pass. The remaining concrete follow-ups are the separately tracked operation-record consistency gap and Spec Kit adapter-status specification drift.

## Evidence carried forward from the completed Spec Kit adapter scope review

Current specification, runtime source, integration text, and focused tests agree on the supported Spec Kit authorization path:

- only directly attached structured `Writes:` metadata becomes implementation-scope input; path-looking task prose is ignored;
- `ChangeWriteSet` rejects duplicate task identities, duplicate writes within a task, repeated writes across tasks, and noncanonical write paths;
- implementation authorization requires an explicit non-empty task selection, rejects duplicate or unknown selected IDs, and normalizes selected tasks back into canonical host order;
- the workflow overlay transports the explicit selection through transient `BOUNDARY_TASK_IDS` JSON and invokes `boundary authorize`; the runtime reads that transport only when repeated `--task` arguments were not supplied;
- authorization resolves only the selected tasks through `change.select_tasks(...)`; the feature-wide `change.writes` union remains a planning/preflight projection and is not an authorization fallback;
- verification reads the active historical operation record and does not call `project_change` or otherwise reinterpret current `tasks.md`;
- Spec Kit bookkeeping classification cannot hide a native contract or a path already present in `authorizedTargets`, because core verification forces both classes back into checked writes before consulting the adapter classifier;
- declared-scope preflight reparses the current structured change, loads the current native contract graph, resolves the complete declared write union, and blocks malformed, ambiguously owned, or unowned targets without creating authority.

The old Review1 behavior—flattening every task in the active feature into one implicit authorization—does not exist in the supported path. A feature-wide ordered union still exists as `ChangeWriteSet.writes` for planning and declared-scope preflight, but `authorize_implementation()` derives its target list only from the explicit selected task IDs. Omitted selection is a blocking error rather than an all-feature default.

The workflow overlay still has only two blocking Boundary transitions around implementation: `boundary-authorize` before the host implementation step and `boundary-verify` after it. Declared-scope preflight is task-readiness work and may fail when invoked, but it is neither operation evidence nor another Boundary authorization phase.

Focused adapter/authorization coverage passed 40 tests. Relevant regressions include directly attached `Writes:` parsing, explicit/canonical task selection, T009/T012 selected-unit behavior, sequential units within one change, same-owner undeclared-write rejection, adapter-bookkeeping exclusion, and machine-readable unowned-write outcomes.

This pass found no new current-source contradiction. The previously tracked operation-record self-consistency gap and Spec Kit adapter-status specification drift remain separate follow-ups for the drift pass.

## Evidence carried forward from the completed workflow/process-record review

Current specifications and canonical procedure intentionally do not introduce a universal Boundary "workflow record" ownership category. A checkpoint, continuation record, feedback record, or similar durable project artifact is an ordinary repository write unless the active change system genuinely owns the path as its bookkeeping. Native ownership remains generic explicit contract ownership; cross-feature location, workflow importance, and document type do not create special authority.

The supported planning path now addresses the original late-surprise problem before authorization when task refinement follows the current contract. `boundary-scope` guidance and the Spec Kit task preset require implementation tasks to include durable project/workflow records in exact structured `Writes:` metadata. The declared-scope preflight then projects the complete ordered write union, loads the fresh native contract graph, resolves every declared target through Boundary context, and rejects invalid, ambiguously owned, or unowned targets. The concrete `preflight_declared_scope()` implementation performs those checks, and focused tests cover the declared union plus an unowned declared target. The supplied focused run covering the scope skill, Spec Kit projection, native verification, and lifecycle outcomes passed 21 tests.

This is earlier detection, not automatic discovery or ownership. Declared-scope preflight is deliberately not a heuristic search for every file implementation might later decide to edit. If task generation omits a required durable record entirely, preflight has no undeclared target to inspect; the path remains unauthorized and an actual write is still rejected by Git-derived verification. The intended prevention mechanism is therefore explicit planning plus preflight, while deterministic verification remains the final enforcement layer.

Spec Kit bookkeeping classification does not special-case cross-feature workflow records. The concrete classifier treats `.specify/**` and the active feature tree as change-system state; a path such as the historical `specs/CONTINUATION.md` outside the active feature remains an ordinary write. Core verification also prevents adapter classification from hiding native contract files or explicitly authorized targets. Cross-feature records therefore receive no product-level exemption or alternate permission semantics.

The historical project-local `project-records` contract remains the expected kind of solution: the project deliberately gives its durable records explicit native ownership and task generation declares their exact writes. That contract is a project semantic choice, not a Boundary built-in category. Review1 section 9 is therefore addressed by a stable ordinary-write model plus earlier task-generation/preflight detection, rather than by automatic workflow-record ownership. No current README/specification correction or new implementation gap was demonstrated by this pass.

## 5. Close the original runtime/setup incidents that informed the review

Cross-check the source `BOUNDARY-FEEDBACK.md` incidents against current behavior.

Investigate:

- Spec Kit script-mode selection and preservation;
- Bash mode not requiring PowerShell;
- deliberate `BOUNDARY_SPECKIT_SCRIPT=sh|ps|py` transitions;
- runtime prerequisite validation for the selected mode;
- supported host lifecycle use instead of direct generated-script patching;
- treatment of inactive script variants after a mode transition;
- the `.gitignore` scope-discovery incident and whether current planning/preflight guidance would surface such an undeclared/unowned target earlier;
- the Spec Kit `BRANCH`/feature-name metadata ambiguity and whether it is a Boundary concern, a host semantic, or now irrelevant to Boundary's active-feature projection.

Do not claim Boundary solved a host-owned Spec Kit behavior unless Boundary now has an explicit contract or adapter dependency that removes the ambiguity.

## 6. Verify persistent-contract and scope-expansion separation

Use the current lifecycle, authorization, and contract specifications plus implementation/tests to verify the safety properties Review1 wanted preserved:

- undeclared writes are still rejected;
- contract files cannot be modified by implementation operations;
- contract evolution cannot simultaneously authorize dependent implementation;
- changed contract/ownership context can block verification;
- additional required writes require a deliberate transition and fresh authorization;
- current planning state cannot rewrite historical authorization;
- verification remains Git-derived and historical rather than trust-based.

This section should make clear which friction was intentionally retained because it is part of Boundary's enforcement model.

## 7. Check documentation, contracts, implementation, and tests for drift

After the semantic review, compare the public README, focused specifications, native contracts, canonical skills, Spec Kit integration text, implementation, and tests.

Look specifically for stale concepts from Review1's old model:

- feature-wide flattened authorization;
- synthetic task authority identities;
- persisted feature Change Boundaries;
- refresh-time context fingerprint sidecars;
- a separate validation lifecycle stage;
- copied runtime discovery;
- Boundary-owned revision locks;
- project-local launchers;
- PowerShell-only adapter assumptions;
- implicit scope expansion.

Search outside `docs/history/`. Historical material may describe those concepts but must not define current behavior.

Any discovered current-source contradiction should become a concrete follow-up TODO item rather than being papered over in the review.

Resolve the operation-record internal-consistency gap found during implementation-unit review: determine whether persisted implementation records must reject `authorizedTargets` that do not exactly match the selected task-write union or that omit required owner/effective-context evidence. If corrected, add focused regression coverage and reflect the resulting status in the final review.

Resolve the concrete Spec Kit status-query drift found during the active-worker review: `docs/spec-change-adapter.md` says the adapter exposes a non-blocking handoff plus active-feature match, while the current runtime implements authorization/verification and product-level `boundary status` but no adapter status projection. Either implement the documented adapter query with focused coverage or narrow the specification if provider-neutral status plus lifecycle feature checks are the intended final design.

## 8. Produce the follow-up review

Create a new standalone review document at `BOUNDARY-FEEDBACK-REVIEW2.md`. Do not overwrite or extend `BOUNDARY-FEEDBACK-REVIEW1.md`; Review1 remains historical evidence.

The new review must be understandable without replaying the original session and must identify Review1 as a historical input rather than current authority.

Structure `BOUNDARY-FEEDBACK-REVIEW2.md` around:

1. an executive status table mapping every Review1 concern/question to `addressed`, `partially addressed`, `superseded / intentionally out of scope`, or `unresolved`;
2. the current implementation-unit model;
3. the T012 / `clipboard.rs` regression scenario under current semantics;
4. lifecycle and worker-handoff changes;
5. CLI/distribution ergonomics changes;
6. workflow-record and planning/preflight treatment;
7. machine-readable outcome/orchestration treatment;
8. original runtime/setup incident closure;
9. remaining gaps and explicitly rejected design directions.

For each substantive status claim, identify the current specification and concrete implementation/test evidence. Avoid treating the historical review's interpretation as current truth.

Keep recommendations limited to gaps actually demonstrated by current evidence. Do not reopen design questions that the approved current specification has already answered unless implementation or tests contradict it.

## 9. Final consistency and validation

After the review is complete:

- update README/spec references only if the review uncovers an actual current documentation inconsistency;
- keep review/history material clearly non-authoritative relative to `docs/spec*.md` and native contracts;
- run contract validation;
- run focused tests for any behavior inspected or changed;
- run the full suite if source or canonical specifications were changed;
- run legacy-reference and invocation-leak searches;
- run `git diff --check`;
- ensure changed code/documentation files remain at or below 250 lines;
- update `files.include` for the next remaining review area instead of carrying all evidence files indefinitely;
- remove completed checklist sections from this TODO as they are finished.

Baseline at the start of this review-planning iteration: native contract validation passed with 15 contracts, focused distribution coverage passed 9 tests, the complete suite passed 101 tests, and `git diff --check` passed.
