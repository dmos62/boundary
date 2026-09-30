# Boundary Specification

Status: target architecture approved; native Boundary runtime active; task-selected implementation units active

Project type: persistent-contract and operation-authorization infrastructure for coding agents

## Purpose

Boundary provides durable project contracts, effective target context, explicit operation scope, authorization evidence, and verification for agentic software changes.

Boundary is independent of the systems used to describe and execute an individual change.

Spec Kit and agent-runtime integrations are adapters rather than product identities.

The core relationship is:

> A change system owns feature intent and execution state. Boundary owns persistent system contracts and operation authority. Agent adapters deliver relevant procedure and effective context.

## Product concepts

Boundary has the following durable concepts:

- persistent project contracts;
- explicit path ownership;
- additive scoped contract applicability;
- effective target context;
- explicit implementation units selected from structured change tasks;
- explicit implementation write scope;
- implementation authorization;
- historical operation evidence;
- persistent-contract evolution;
- actual-write verification;
- progressive agent instruction disclosure;
- source-revision-pinned downstream installation.

These concepts must remain meaningful if the current change system or agent runtime is replaced.

## Canonical state

The Boundary-defined portion of downstream canonical state consists of:

- change-system artifacts that define the requested change;
- native Boundary contracts under `contracts/`;
- one `boundary.lock.json` pinning the exact Boundary Git revision adopted by the project.

A host change system may own additional persistent project configuration or shareable generated state. Boundary does not reclassify such host-owned state merely because Boundary installation or integration lifecycle commands update it.

Generated Boundary integration state, effective-context projections, installed Boundary skills, the project-local Boundary launcher, caches, install provenance, and operation evidence are not persistent system contracts.

Operation evidence is historical workflow state stored outside ordinary project source, preferably in current-worktree Git metadata.

The Boundary lock records the expected Boundary source revision but is not a source-distribution locator. Operators supply a Boundary source checkout separately when running downstream lifecycle commands.

Current Spec Kit project-state ownership and generated-state boundaries are defined in [spec-distribution-state.md](spec-distribution-state.md).

## Native persistent contracts

Boundary defines a native contract format.

Contract files:

- have explicit repository-relative scope;
- have stable contract identifiers;
- may own exact paths or subtrees;
- may apply constraints to additional explicit scopes;
- may declare architecture dependencies;
- contain concise human-readable invariants, prohibitions, and interfaces.

Contract file placement has no semantic effect.

The native model does not use directory walking, nearest-file replacement, or a global catch-all project contract.

Detailed contract semantics are defined in [spec-contracts.md](spec-contracts.md).

## Additive applicability invariant

A target may be governed by several contracts.

All matching contracts apply additively.

When ownership is nested, the most specific matching owner is the target's primary owner, while broader matching owning contracts continue to contribute constraints.

A more specific contract therefore cannot silently free a target from a broader applicable contract.

Boundary v1 has no contract override or exception mechanism.

## Explicit write-scope invariant

Implementation authority must never be inferred from path-looking prose.

The change-system adapter must provide explicit write declarations for implementation tasks or their equivalent structured operation input.

Planning may heuristically inspect path mentions for advisory context. Authorization may not use those heuristics.

Every authorized implementation target must resolve to one unambiguous primary owner under the fresh native contract graph.

Authorization covers only writes belonging to the explicitly selected implementation unit. Writes declared by other tasks in the same change do not become authorized merely because they are present in the active change.

## Implementation-unit invariant

A change may contain several implementation units.

For the provider-neutral Boundary model, one implementation unit is an explicit ordered selection of one or more task identities from the active change. Its write set is the deterministic ordered union of the structured writes of those selected tasks.

Implementation-unit selection is operation input, not a second persistent change specification. The operation record is the durable historical evidence of which task identities and targets were authorized.

A unit may span one or several architectural owners when the change genuinely requires coordinated work. Boundary records the resolved ownership of every target rather than silently splitting or widening the unit.

Selecting all tasks in a change is allowed only when that selection is explicit. Feature-wide authorization is not an implicit default.

Discovering an additional required write never widens the active unit. If the path is already declared by an unselected task, the operation must transition out and a fresh authorization may select that task as part of the next unit. If the path is not declared by any task, the change system must first update structured scope before fresh authorization.

Same-owner discovery and cross-owner discovery may produce different coordination diagnostics, but neither grants implicit write authority.

## Operation separation invariant

Implementation and persistent-contract evolution are different operation kinds.

An implementation operation may not modify native contract files.

A contract-evolution operation may not use its changed contracts to authorize implementation writes in the same operation.

Dependent implementation begins only after contract evolution is validated and a fresh implementation authorization succeeds.

## Authorization invariant

Authorization derives current operation scope directly from:

- the active change identity;
- the explicit task identities selected for the implementation unit;
- canonical structured write declarations for those tasks;
- a freshly loaded native contract graph;
- current Git state.

It does not depend on a previously generated feature boundary or refresh-time fingerprint sidecar.

Successful authorization creates one atomic operation record containing all evidence required by later verification, including the selected task identities and resolved authorized targets.

Mutable planning state cannot widen that record retroactively.

A compact authorization-state handoff may be derived from current operation evidence for agent transfer. It is transient query output and never becomes another authority source.

## Agent-context invariant

Boundary does not require a large framework bootstrap or the complete project contract set in normal agent context.

Stable procedure belongs in small reusable skills.

Operation-specific facts belong in deterministic query results.

Persistent contract prose is disclosed only when relevant to the current target or relationship.

A tiny stable set of Boundary behavioral invariants may be always available, but project-specific architecture must not be permanently injected.

## Adapter model

Boundary has two permanent integration boundaries:

- a change-system adapter;
- an agent-runtime adapter.

The current concrete integrations are Spec Kit for change-system state and Codex plus Claude Code materializers for agent procedure.

The change-system adapter projects ordered structured tasks and accepts explicit implementation-unit selection at implementation entry. It does not flatten the whole active change into implicit implementation authority.

Boundary does not introduce a generalized runtime provider-plugin framework merely to abstract these implementations. Concrete adapters are preferred until actual implementations demonstrate a useful stable shared interface.

## Downstream source-checkout invariant

A downstream repository records the exact Boundary Git revision it expects but does not carry canonical Boundary implementation source.

Downstream lifecycle commands are executed from an operator-supplied Boundary source checkout. Except when first adopting or deliberately upgrading Boundary, that checkout must be clean and its exact Git revision must equal the committed lock.

The downstream consumer does not fetch Boundary source, resolve releases, follow branches or tags, or reconstruct source from a remote locator stored in the project.

Generated runtime, extension, preset, workflow, Boundary skill, and project-local launcher state is recreated from the supplied matching checkout and does not become canonical Boundary implementation source in the consumer project.

Adoption records the revision of the Boundary checkout being used. Upgrades are performed deliberately from a different clean Boundary checkout and replace the lock only after candidate installation succeeds.

Detailed downstream lifecycle semantics are defined in [spec-distribution.md](spec-distribution.md), with project-state ownership defined in [spec-distribution-state.md](spec-distribution-state.md).

## Non-goals

Boundary does not:

- replace a product requirements or feature-specification system;
- require Spec Kit as its permanent change system;
- preserve migration-provider semantics merely for compatibility;
- require legacy provider state downstream;
- maintain a second compiled persistent copy of project contracts;
- authorize writes from prose path mentions;
- formalize all architectural prose into executable rules;
- make agent prompt compliance the enforcement layer;
- create a global catch-all cross-contract prompt;
- provide implicit contract override semantics;
- introduce a generalized adapter marketplace or plugin framework;
- automatically evolve persistent contracts to make implementation pass;
- infer an implementation unit from architectural ownership;
- silently authorize every task in the active change;
- fetch or discover Boundary source on behalf of a downstream project;
- encode operator-local Boundary checkout paths in canonical project state.

## Focused specifications

The design is split by responsibility:

- [spec-architecture.md](spec-architecture.md): core structures, adapters, transient projections, and deterministic boundaries.
- [spec-contracts.md](spec-contracts.md): native contract syntax and semantic model.
- [spec-agent-instructions.md](spec-agent-instructions.md): skill architecture and progressive disclosure.
- [spec-authorization.md](spec-authorization.md): explicit writes, implementation-unit authorization, operation records, Git baselines, epochs, verification, and authorization-state handoff.
- [spec-change-adapter.md](spec-change-adapter.md): provider-neutral change-system projection, task-selected implementation units, and Spec Kit integration.
- [spec-lifecycle.md](spec-lifecycle.md): integration with change systems, contract evolution, implementation-unit transitions, and convergence.
- [spec-distribution.md](spec-distribution.md): source-checkout-driven downstream adoption, installation, health checking, removal, and upgrades.
- [spec-distribution-state.md](spec-distribution-state.md): downstream canonical state, Spec Kit project-state ownership, and Boundary generated-state exclusions.

Historical migration material is isolated under [history/](history/) and is not part of the current product architecture.

## Migration status

Native Boundary semantics have replaced the migration-era provider path.

The supported runtime no longer depends on:

- persisted feature Change Boundaries;
- refresh-time context fingerprint sidecars;
- a separate public validation lifecycle stage;
- synthetic task authority identities;
- mixed implementation/specification authorization;
- split authorization evidence;
- project-wide provider bootstrap injection;
- duplicated extension-hook and workflow-overlay enforcement;
- feature-wide flattened implementation authorization.

The Spec Kit adapter now requires explicit task selection and persists the selected task identities with the immutable operation target set.

Downstream installations now expose a generated project-local semantic Boundary command that hides runtime and adapter packaging from normal agent procedure.

Declared-scope preflight now surfaces invalid, unowned, or ambiguously owned structured writes before implementation entry, and blocking adapter results expose stable machine-readable lifecycle outcomes.

A compact provider-neutral authorization-state handoff is available to integrations without creating another authorization artifact or lifecycle stage.

Remaining release work includes canonical status exposure for that handoff, compatibility cleanup, and final verification.

## Summary invariant

Boundary remains coherent while:

> project contracts are canonical and independently scoped; change systems provide explicit change intent and ordered task writes; implementation authority is limited to explicitly selected task units; skills provide procedure; queries provide current facts; deterministic code provides authorization and verification; and downstream tooling is supplied from a clean Boundary checkout whose revision matches the project's committed source pin.
