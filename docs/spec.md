# Boundary Specification

Status: target architecture approved; native Boundary runtime active; task-selected implementation units active; mise-native distribution transition approved

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
- mise-managed downstream tool selection and installation.

These concepts must remain meaningful if the current change system or agent runtime is replaced.

## Canonical state

Boundary-defined persistent downstream semantics consist of:

- change-system artifacts that define the requested change;
- native Boundary contracts under `contracts/`.

A host change system may own additional persistent project configuration or shareable generated state. Boundary does not reclassify such host-owned state merely because Boundary installation or integration lifecycle commands update it.

Project tooling may also contain Boundary distribution configuration in mise-managed files such as `mise.toml` and `mise.lock`. Those files are normal project/tooling state, not Boundary persistent contracts and not a second Boundary-owned contract format.

Generated Boundary integration state, effective-context projections, installed Boundary skills, caches, and operation evidence are not persistent system contracts.

Operation evidence is historical workflow state stored outside ordinary project source, preferably in current-worktree Git metadata.

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

## Mise-managed distribution invariant

Boundary is a conventional mise-installable CLI.

Downstream projects use mise configuration and `mise.lock` as their Boundary installation and version-selection state.

The selected Git-backed mise installation model must preserve an exact Boundary Git source identity for locked installation. Boundary does not define another revision lock, dependency lock, source-checkout matching protocol, or package-service bridge.

The complete transitive Python dependency graph is not a Boundary downstream locking requirement. Boundary package metadata defines compatible runtime dependencies, and the mise-selected installation backend resolves those dependencies.

Normal downstream use does not require an operator-supplied Boundary checkout. A local Boundary checkout is a development input rather than portable downstream project state.

The installed `boundary` executable is the canonical downstream command surface. Generated project-local launchers must not exist solely to locate copied Boundary runtime packages.

Detailed distribution semantics are defined in [spec-distribution.md](spec-distribution.md), with project-state ownership defined in [spec-distribution-state.md](spec-distribution-state.md).

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
- define a second Boundary-owned revision or dependency lock beside mise;
- require portable project state to contain operator-local source paths;
- require a frozen transitive Python dependency graph for the Boundary tool;
- wrap mise with a second package-management protocol.

## Focused specifications

The design is split by responsibility:

- [spec-architecture.md](spec-architecture.md): core structures, adapters, transient projections, and deterministic boundaries.
- [spec-contracts.md](spec-contracts.md): native contract syntax and semantic model.
- [spec-agent-instructions.md](spec-agent-instructions.md): skill architecture and progressive disclosure.
- [spec-authorization.md](spec-authorization.md): explicit writes, implementation-unit authorization, operation records, Git baselines, epochs, verification, and authorization-state handoff.
- [spec-change-adapter.md](spec-change-adapter.md): provider-neutral change-system projection, task-selected implementation units, and Spec Kit integration.
- [spec-lifecycle.md](spec-lifecycle.md): integration with change systems, contract evolution, implementation-unit transitions, and convergence.
- [spec-distribution.md](spec-distribution.md): mise-managed downstream installation, source identity, integration materialization, health checking, removal, and upgrades.
- [spec-distribution-state.md](spec-distribution-state.md): downstream canonical semantics, project tooling state, Spec Kit ownership, and Boundary generated-state exclusions.

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

Declared-scope preflight surfaces invalid, unowned, or ambiguously owned structured writes before implementation entry, and blocking adapter results expose stable machine-readable lifecycle outcomes.

A compact provider-neutral authorization-state handoff is available to integrations without creating another authorization artifact or lifecycle stage.

Canonical `boundary status` exposes that compact handoff directly.

The approved distribution transition replaces Boundary-owned revision locking and copied-runtime discovery with mise-managed Git source selection and an installed `boundary` console entry point.

## Summary invariant

Boundary remains coherent while:

> project contracts are canonical and independently scoped; change systems provide explicit change intent and ordered task writes; implementation authority is limited to explicitly selected task units; skills provide procedure; queries provide current facts; deterministic code provides authorization and verification; and downstream Boundary tooling is selected, locked, installed, and upgraded through mise using normal project tooling state.
