# Boundary Lifecycle Semantics

Boundary integrates with a change process without making that process part of its product identity.

The current change-system adapter is Spec Kit. Another change system, or a future Boundary-native change workflow, must be able to drive the same Boundary lifecycle.

## Mandatory implementation lifecycle

Boundary's mandatory lifecycle is:

    authorize → implement → verify

Each implementation authorization operates on one explicitly selected implementation unit.

Planning and task generation may use Boundary context, but they do not establish implementation authority. Persisted context refresh and separate validation gates are not part of the supported Boundary lifecycle.

## Planning

During planning an agent may inspect candidate target contracts, identify ownership, discover applicable invariants and interfaces, classify likely contract evolution, and refine implementation paths.

Planning context is advisory. Heuristic path discovery is acceptable because planning output cannot grant write permission. No feature-local authorization artifact is created.

## Task generation

Before tasks are implementation-ready, the change-system adapter supplies explicit write declarations.

The Boundary scope skill helps the agent name exact intended writes, inspect their effective context, separate contract evolution from implementation, prefer coherent owner-local tasks where useful, and include durable workflow records when implementation is expected to update them.

A checkpoint, continuation record, feedback record, or similar durable project artifact is an ordinary write unless the active change system actually owns it as bookkeeping. Workflow importance does not exempt such a path from structured declaration or native contract ownership.

After structured task writes are available, the host integration should run a non-authorizing declared-scope preflight over their deterministic ordered union. It uses Boundary target inspection to surface invalid, unowned, or ambiguously owned targets before implementation entry.

Declared-scope preflight is task-readiness information only. It creates no operation record, captures no Git authorization baseline, selects no implementation unit, and grants no authority. Later authorization independently reloads current task state, contracts, and Git state and considers only explicitly selected tasks.

A user story or coordinated task may span several owners. Boundary v1 does not require a synthetic task authority identity.

## Authorization

Authorization is the blocking transition into implementation.

It uses a fresh ordered change-task projection, explicit selected task identities, only the structured writes of those selected tasks, fresh native contracts, and current Git state.

It does not refresh an earlier boundary or reuse an earlier planning or declared-scope diagnostic as authorization evidence. Missing task selection is a failure; omission never means the complete active change.

Successful authorization creates the historical operation record consumed by verification. An existing unverified operation cannot be silently replaced by another authorization epoch.

## Implementation

Implementation runs under one active implementation operation.

The implementation skill directs the agent to inspect relevant effective contract context, modify only authorized targets, stop before scope expansion, and transition out of implementation when persistent contracts need evolution.

Deterministic checks remain authoritative even if an agent fails to follow the skill. A Git `HEAD` transition during an active operation invalidates the baseline and prevents successful verification.

## Scope expansion

When implementation discovers another required target:

1. inspect it if needed, but do not write it under the current operation;
2. verify and close the current operation;
3. update structured task scope when necessary;
4. explicitly select the fresh implementation unit;
5. authorize a new operation;
6. carry forward verified predecessor state only when its exact Git state is unchanged.

A verified predecessor is archived only when the successor actually relies on carry-forward evidence. Scope expansion preserves valid completed work but always requires an explicit authorization epoch transition, regardless of whether the discovered target shares the current unit's owner.

## Verification

Verification compares actual Git changes with the historical operation record.

It does not use current task prose, current task selection, current planning projections, or a regenerated feature boundary.

Verification reports authorization correctness only. Successful verification closes the current epoch by marking its operation record verified and recording final dirty-state identities for authorized targets. Those identities are the only provenance accepted for dirty-target carry-forward.

Feature correctness and broader convergence are separate.

## Machine-readable lifecycle outcomes

Blocking Boundary results expose stable machine-readable lifecycle semantics in addition to human-readable diagnostics.

The version-1 blocked outcome contains `schema: boundary.lifecycle-outcome/v1`, `status: blocked`, the lifecycle stage, one stable category, one structured diagnostic code, the human-readable message, available change and operation identities, structured diagnostics when produced by the underlying check, and an optional required Boundary transition.

Stable categories include:

- `scope-expansion-required`;
- `contract-evolution-required`;
- `invalid-adapter-state`;
- `missing-external-prerequisite`;
- `stale-authorization`;
- `verification-write-scope-failure`.

Verification keeps its historical semantics when producing these outcomes. An undeclared or unowned actual write remains a verification failure; current mutable task state is not consulted to reinterpret or authorize it. The outcome may additionally identify the required Boundary transition.

Declared-scope preflight uses the same vocabulary where applicable but never contains an operation identity because preflight creates no operation.

Structured outcomes describe Boundary state and required Boundary lifecycle transitions. They do not decide whether an outer controller should pause, retry, ask a human, or continue another activity.

## Contract evolution

When requested behavior cannot satisfy current persistent contracts:

1. stop dependent implementation;
2. verify and close the current implementation operation, or abandon it through an explicit future lifecycle mechanism;
3. begin a `contract-evolution` operation;
4. use the Boundary contracts skill;
5. modify only native contract files;
6. run `boundary contracts check`;
7. verify and close contract evolution;
8. explicitly select the dependent implementation unit;
9. authorize dependent implementation against the resulting fresh graph.

Contract evolution never retroactively authorizes earlier implementation.

## Convergence

Boundary distinguishes:

- operation correctness: actual writes matched historical authorization;
- contract structural correctness: the native contract graph is valid;
- feature correctness: implementation satisfies requested behavior;
- semantic system correctness: implementation respects applicable prose contracts;
- development governance: the active change system's process rules are satisfied.

Only the first two are fully deterministic Boundary-core concerns in v1. A concrete change system may impose additional governance without making it a Boundary architectural layer.

## Product CLI direction

The canonical product-level command surface should converge toward:

    boundary inspect <target...>
    boundary contracts check
    boundary authorize
    boundary verify
    boundary status

Additional status or debugging commands may be introduced when justified. These commands use Boundary terminology and do not depend on a particular change system.

Installed downstream projects materialize the semantic surface at `.boundary/bin/boundary`. That generated command self-locates installed Boundary runtime state and delegates change-system-specific authorization and verification translation to the active adapter. Its filesystem location is installation detail rather than a second product API.

Declared-scope preflight composes the existing `boundary inspect` query over structured targets. It does not add another mandatory Boundary lifecycle phase or require a persisted preflight artifact.

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

Before that lifecycle begins, Spec Kit task refinement should inspect the complete structured write projection and surface ownership defects. This readiness check remains outside the blocking Boundary lifecycle and supplies no authorization evidence.

The workflow overlay receives explicit task selection through transient adapter input and has no implicit whole-feature selection.

Planning and task augmentations may invoke Boundary skills and inspection, but they do not create redundant structural gates.

## Workflow overlay

The supported Spec Kit integration uses one deterministic structural-enforcement mechanism: the workflow overlay.

Its ordering and nonzero shell status make authorization and verification transitions explicit.

Installed downstream workflows invoke the generated semantic Boundary command when available. Development installations may fall back to the concrete adapter gate so source-development bootstrap remains separate from downstream consumer materialization.

Extension hooks do not duplicate those gates.

## Preset role

The Spec Kit preset is intentionally narrow.

Its task-generation augmentation directs task refinement toward exact write declarations, calls out required durable workflow records as explicit writes rather than implicit administrative state, permits on-demand `boundary inspect`, uses target inspection to surface ownership defects before implementation entry, keeps contract evolution separate, and requires fresh authorization after scope change.

It does not create planning context state, a validation phase, or convergence-time authorization semantics.

## Adapter replacement

Replacing Spec Kit must require only a new change-system adapter that can provide the active change identity, ordered structured tasks and exact writes, explicit implementation-unit task selection, lifecycle calls around implementation, and classification of its own generated or change artifacts.

Native contracts, skills, authorization semantics, and Git verification remain unchanged.
