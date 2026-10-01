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

## 2. Review lifecycle and mechanical invocation overhead

Evaluate Review1 sections 4, 5, and 6 against the current CLI and distribution model.

Confirm that normal use now has stable semantic entrypoints for:

- effective-context inspection;
- implementation authorization;
- verification;
- current authorization status;
- contract validation;
- integration install/check/remove.

Verify that normal downstream use no longer requires:

- `PYTHONPATH`;
- direct `python -m boundary` invocation;
- uv cache plumbing;
- locating `adapter_gate.py`;
- locating copied Boundary runtime source;
- a generated project-local Boundary launcher;
- an operator-supplied Boundary checkout.

Trace the installed CLI through package metadata and packaged integration assets sufficiently to show that the documented command surface is real rather than merely aspirational.

Classify the mechanical-discovery concern separately from the implementation-unit concern so the review does not conflate architectural improvement with packaging improvement.

## 3. Review Spec Kit adapter scope projection and lifecycle gates

Inspect the current adapter implementation, command wrappers, workflow overlay, and relevant tests.

Verify that:

- structured task writes are the only implementation-scope input;
- incidental path-looking prose is ignored for authorization;
- explicit task selection is required;
- duplicate/unknown/empty task selections fail deterministically;
- the workflow transport preserves explicit selected task IDs rather than reconstructing feature-wide scope;
- implementation entry and exit remain the only blocking Boundary lifecycle transitions;
- current task state is not reused as historical authorization evidence during verification;
- adapter bookkeeping classification cannot hide an authorized target or native contract write;
- declared-scope preflight can expose malformed, unowned, or ambiguously owned writes before implementation entry.

Compare this directly with Review1's description of the old feature-wide flattened authorization and state whether that behavior still exists anywhere in the supported path.

## 4. Review workflow/process-record treatment

Revisit Review1 section 9 and the original `specs/CONTINUATION.md` / `BOUNDARY-FEEDBACK.md` incident.

Determine whether the current system now prevents that class of surprise early enough by examining:

- scope-planning skill guidance;
- Spec Kit task-generation guidance/preset material;
- declared-scope preflight;
- ownership requirements for every implementation target;
- treatment of change-system bookkeeping versus ordinary repository writes.

Answer explicitly:

- whether Boundary introduced any first-class universal "workflow record" ownership category;
- whether such files instead remain ordinary project-authored targets requiring explicit contract ownership and structured task writes;
- whether the updated planning/preflight path is sufficient to catch missing ownership before implementation authorization;
- whether cross-feature records receive any special treatment;
- whether the original project-local `project-records` contract remains the expected kind of solution rather than a product-level special case.

If the concern is intentionally solved by earlier detection rather than automatic ownership, state that distinction.

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

Write one focused review document that is understandable without replaying the original session.

Structure it around:

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
