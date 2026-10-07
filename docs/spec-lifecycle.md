# Boundary Lifecycle Semantics

Boundary integrates with a change process without making that process part of its product identity.

The current change-system adapter is Spec Kit. Another change system, or a future Boundary-native change workflow, must be able to drive the same Boundary lifecycle.

## Mandatory implementation lifecycle

Boundary's mandatory lifecycle is:

    authorize → implement → verify

Each implementation authorization operates on one explicitly selected implementation unit.

For routine direct CLI use the smallest workflow is:

    boundary authorize T012 [T013 ...]
    boundary inspect --authorized
    implement and run ordinary project checks
    boundary verify

In lifecycle-gated integrations, authorization may be performed by the coordinator or workflow. The implementation worker then normally needs only `boundary inspect --authorized` before editing.

Planning and task generation may use Boundary context, but they do not establish implementation authority. Persisted context refresh and separate validation gates are not part of the supported Boundary lifecycle.

Tool installation and generated project integration are prerequisites around this lifecycle rather than authorization phases.

## Planning

During planning an agent may inspect candidate target contracts, identify ownership, discover applicable invariants and interfaces, classify likely contract evolution, and refine implementation paths.

Planning context is advisory. Heuristic path discovery is acceptable because planning output cannot grant write permission. No feature-local authorization artifact is created.

## Task generation

Before tasks are implementation-ready, the change-system adapter supplies explicit write declarations.

The Boundary scope skill helps the agent name exact intended writes, inspect their effective context, separate contract evolution from implementation, prefer coherent owner-local tasks where useful, and include durable workflow records when implementation is expected to update them.

A checkpoint, continuation record, feedback record, or similar durable project artifact is an ordinary write unless the active change system actually owns it as bookkeeping. Workflow importance does not exempt such a path from structured declaration or native contract ownership.

After structured task writes are available, the host integration should run a non-authorizing declared-scope preflight over their deterministic ordered union. It uses Boundary target inspection to surface invalid, unowned, or ambiguously owned targets before implementation entry.

Declared-scope preflight is task-readiness information only. It creates no operation record, captures no Git authorization baseline, selects no implementation unit, and grants no authority.

Later authorization independently reloads current task state, contracts, and Git state and considers only explicitly selected tasks.

A user story or coordinated task may span several owners. Boundary v1 does not require a synthetic task authority identity.

## Authorization

Authorization is the blocking transition into implementation.

It uses a fresh ordered change-task projection, explicit selected task identities, only the structured writes of those selected tasks, fresh native contracts, and current Git state.

It does not refresh an earlier boundary or reuse an earlier planning or declared-scope diagnostic as authorization evidence.

Missing task selection is a failure; omission never means the complete active change. Direct CLI use supplies task IDs positionally. Adapter workflows may transport the same explicit selection separately.

Successful authorization creates the historical operation record consumed by verification and emits a concise lifecycle result rather than serializing that record to routine stdout.

An existing unverified operation cannot be silently replaced by another authorization epoch.

## Implementation

Implementation runs under one active implementation operation.

`boundary inspect --authorized` is the routine implementation-entry query. It requires a current authorized implementation operation with a matching Git baseline, uses the historical authorized target set, fresh-resolves effective Boundary context, and renders the unit identity and target context in one invocation.

The implementation skill directs the agent to modify only those authorized targets, preserve all applicable constraints, stop before scope expansion, and transition out of implementation when persistent contracts need evolution.

`boundary status` remains available for recovery, handoff, and debugging. It is not an additional routine implementation prerequisite when authorized-unit inspection has already established operation identity, baseline freshness, target scope, and current effective context.

Deterministic checks remain authoritative even if an agent fails to follow the skill.

A Git `HEAD` transition during an active operation invalidates the baseline and prevents successful verification.

## Scope expansion

When implementation discovers another required target:

1. inspect it if needed, but do not write it under the current operation;
2. verify and close the current operation;
3. update structured task scope when necessary;
4. explicitly select the fresh implementation unit;
5. authorize a new operation;
6. carry forward verified predecessor state only when its exact Git state is unchanged.

A verified predecessor is archived only when the successor actually relies on carry-forward evidence.

Scope expansion preserves valid completed work but always requires an explicit authorization epoch transition, regardless of whether the discovered target shares the current unit's owner.

## Verification

Verification compares actual Git changes with the historical operation record.

It does not use current task prose, current task selection, current planning projections, or a regenerated feature boundary.

Verification reports authorization correctness only.

Successful verification closes the current epoch by marking its operation record verified and recording final dirty-state identities for authorized targets.

Those identities are the only provenance accepted for dirty-target carry-forward.

The routine verify command emits a concise lifecycle result and does not dump verification path-state fingerprints.

Feature correctness and broader convergence are separate.

## Machine-readable lifecycle results

Authorize and verify results use `schema: boundary.lifecycle-result/v1`.

Every result contains `status`, `stage`, and a structured `diagnostics` collection. Successful results contain an explicit empty diagnostics collection and available operation/change identity. Authorization success additionally contains selected task identities and exact authorized target paths. Verification success contains selected task identities when applicable.

Blocked results use `status: blocked` and additionally expose one stable category, one structured diagnostic code, the human-readable message, available change and operation identities, structured diagnostics, and an optional required Boundary transition.

Stable blocked categories include:

- `scope-expansion-required`;
- `contract-evolution-required`;
- `invalid-adapter-state`;
- `missing-external-prerequisite`;
- `stale-authorization`;
- `verification-write-scope-failure`.

Blocking lifecycle commands retain nonzero process exit status. Consumers do not need a wrapper or output-filtering pipeline to preserve failure semantics.

Verification keeps its historical semantics when producing these results.

An undeclared or unowned actual write remains a verification failure; current mutable task state is not consulted to reinterpret or authorize it.

Structured results describe Boundary state and required Boundary lifecycle transitions. They do not decide whether an outer controller should pause, retry, ask a human, or continue another activity.

## Contract evolution

When requested behavior cannot satisfy current persistent contracts:

1. stop dependent implementation;
2. verify and close the current implementation operation, or abandon it through an explicit future lifecycle mechanism;
3. authorize exact native contract targets with `boundary contracts authorize --change CHANGE_ID CONTRACT...`;
4. use the Boundary contracts skill;
5. modify only the authorized native contract files;
6. run `boundary contracts check`;
7. verify and close contract evolution;
8. explicitly select the dependent implementation unit;
9. authorize dependent implementation against the resulting fresh graph.

Contract evolution never retroactively authorizes earlier implementation. When it establishes ownership for an unowned ordinary target, the evolution authorization still covers only native contract files; the ordinary target is written only after closure and fresh implementation authorization.

## Convergence

Boundary distinguishes:

- operation correctness: actual writes matched historical authorization;
- contract structural correctness: the native contract graph is valid;
- feature correctness: implementation satisfies requested behavior;
- semantic system correctness: implementation respects applicable prose contracts;
- development governance: the active change system's process rules are satisfied.

Only the first two are fully deterministic Boundary-core concerns in v1.

A concrete change system may impose additional governance without making it a Boundary architectural layer.

## Product CLI direction

The canonical installed product-level command surface is intentionally small:

    boundary authorize T012 [T013 ...]
    boundary inspect --authorized
    boundary inspect <target...>
    boundary verify
    boundary status
    boundary contracts authorize --change CHANGE_ID CONTRACT...
    boundary contracts check

Boundary-specific generated integration is managed separately through:

    boundary integration install
    boundary integration check
    boundary integration remove

`authorize`, `inspect --authorized`, and `verify` form the routine direct implementation path. Ordinary `boundary inspect <target...>` is situational: planning, undeclared-target investigation, declared-scope preflight, and focused queries.

`boundary status` is a read-only recovery, handoff, and debugging query. It emits the compact `boundary.authorization-handoff/v1` document directly as JSON, or JSON `null` when no current operation exists. It does not select tasks, create operation evidence, replace authorization or verification, or act as installation health checking.

`boundary contracts` and `boundary integration` are maintenance surfaces rather than routine implementation stages.

No compound `boundary next` command is defined. Explicit `verify` followed by explicit `authorize` remains the lifecycle until actual usage demonstrates recurring friction worth additional API and partial-success semantics.

## Spec Kit adapter

The Spec Kit adapter exposes thin agent-facing wrappers:

    speckit.boundary.authorize
    speckit.boundary.verify

Those names belong to the adapter, not the canonical Boundary product API.

The Spec Kit workflow integration enforces a repeatable unit lifecycle:

    tasks
      → explicit unit selection
      → boundary-authorize
      → implement
      → boundary-verify
      → next selected unit when needed

Before that lifecycle begins, Spec Kit task refinement should inspect the complete structured write projection and surface ownership defects.

This readiness check remains outside the blocking Boundary lifecycle and supplies no authorization evidence.

The workflow overlay receives explicit task selection through transient adapter input and has no implicit whole-feature selection.

Planning and task augmentations may invoke Boundary skills and inspection, but they do not create redundant structural gates.

## Workflow overlay

The supported Spec Kit integration uses one deterministic structural-enforcement mechanism: the workflow overlay.

Its ordering and nonzero shell status make authorization and verification transitions explicit.

Installed downstream workflows invoke the installed `boundary` executable.

Development workflows use the same semantic command surface through repository mise tooling.

Extension hooks do not duplicate those gates.

## Preset role

The Spec Kit preset is intentionally narrow.

Its task-generation augmentation directs task refinement toward exact write declarations, calls out required durable workflow records as explicit writes rather than implicit administrative state, permits on-demand `boundary inspect`, uses target inspection to surface ownership defects before implementation entry, keeps contract evolution separate, and requires fresh authorization after scope change.

It does not create planning context state, a validation phase, or convergence-time authorization semantics.

## Adapter replacement

Replacing Spec Kit must require only a new change-system adapter that can provide the active change identity, ordered structured tasks and exact writes, explicit implementation-unit task selection, lifecycle calls around implementation, and classification of its own generated or change artifacts.

Native contracts, skills, authorization semantics, Git verification, and mise-owned Boundary installation remain independent concerns.
