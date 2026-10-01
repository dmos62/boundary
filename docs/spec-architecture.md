# Boundary Architecture

This document defines Boundary's target structural architecture. Contract semantics, agent instruction delivery, authorization evidence, lifecycle transitions, and distribution are documented separately.

## Architectural boundaries

Boundary has four target layers.

### Boundary core

The core owns provider-independent mechanics:

- repository path normalization;
- explicit operation write scope;
- contract-graph queries;
- target ownership projection;
- effective-context composition;
- operation authorization;
- Git operation baselines;
- actual-write verification;
- provider-neutral diagnostics;
- atomic operation evidence.

The core does not know about Spec Kit command names, agent skill directories, legacy specification-provider sections, provider file types, or provider bootstrap state.

### Native contract engine

The native contract engine:

- discovers `contracts/**/*.contract.md`;
- parses contract frontmatter and semantic sections;
- validates path scopes and ownership relationships;
- constructs the in-memory `ContractGraph`;
- resolves `TargetContext`;
- exposes relevant interface context for declared dependencies;
- validates contract-only evolution results.

The graph is rebuilt from canonical contracts. It is not a persistent second source of truth.

### Change-system adapter

A change-system adapter translates an external change workflow into Boundary inputs.

Its responsibilities are limited to concepts such as:

- active change identifier;
- canonical task identity and task order;
- explicit declared write targets;
- explicit implementation-unit task selection;
- adapter-owned feature artifacts;
- lifecycle integration points.

The current concrete adapter is Spec Kit.

Boundary's core semantics do not require Spec Kit-specific stages, files, command syntax, or constitution concepts.

### Agent-runtime adapter

An agent-runtime adapter materializes Boundary's canonical skills and thin entry points for an agent environment.

Codex is the active runtime for the current repository. Its concrete adapter materializes canonical skills under `.agents/skills/` and adds only runtime discovery metadata.

A second concrete Claude Code materializer targets `.claude/skills/`. It exists as portability evidence and test coverage, not as the first member of a generalized runtime-provider framework.

The two adapters deliberately remain concrete. Shared runtime infrastructure should be introduced only when actual divergence or repeated implementation demonstrates a useful stable interface.

Canonical skill content uses Boundary concepts rather than vendor-specific tool syntax. Agent-specific wrappers may map those concepts onto local commands.

## Core data model

The target core operates on a small set of provider-independent structures.

### Contract

A parsed canonical persistent contract containing:

- stable ID;
- source path;
- owned scopes;
- additional applicable scopes;
- declared dependencies;
- semantic sections;
- content identity.

### ContractGraph

An in-memory validated graph containing:

- contracts by ID;
- ownership scope index;
- applicability scope index;
- dependency edges.

The graph is transient and deterministic for equivalent canonical contract contents.

### TargetContext

A derived projection for one repository target:

- target path;
- primary owner;
- applicable contract IDs;
- effective invariants and prohibitions;
- relevant dependency interfaces;
- source provenance.

Target context is query output, not canonical state.

### ChangeContext

Input supplied by a change-system adapter:

- change identifier;
- operation kind;
- ordered task identities and structured writes;
- explicit selected task identities for implementation;
- adapter-owned non-implementation artifacts.

The core never discovers authorization scope from arbitrary prose.

### OperationRecord

Historical evidence for one authorized operation:

- operation identifier;
- change identifier;
- operation kind;
- selected task identities for implementation;
- exact authorized targets;
- target ownership/effective-context identities;
- Git `HEAD`;
- dirty-path baseline;
- predecessor/carry-forward evidence when applicable;
- lifecycle status.

One operation is represented by one atomic document.

## Source and package layout direction

The canonical implementation should retain provider-neutral package boundaries similar to:

    src/boundary/
      contracts/
      context/
      authorization/
      verification/
      cli/

    skills/
      scope/
      implement/
      contracts/

    adapters/
      codex/
      claude/

    integration/
      speckit/

    schemas/

Boundary source must also carry conventional Python package metadata exposing the `boundary` console entry point.

Repository mise configuration and tasks own the source-development tool environment.

Downstream mise configuration owns selection of the installed Boundary tool and is not copied into Boundary core semantics.

Installed/generated integration state remains separate from canonical source.

## Distribution boundary

Mise owns downstream Boundary source selection and tool installation.

Boundary's package metadata owns Python dependency compatibility declarations.

The installed `boundary` executable owns the public Boundary command surface.

Boundary integration code may materialize generated change-system and agent-runtime state, but it does not own a second package manager, source lock, or copied-runtime locator.

A local Boundary source checkout is a development concern rather than a required downstream runtime input.

## Deterministic versus agentic responsibility

Deterministic code owns facts that can be computed reliably:

- valid path syntax;
- contract parsing;
- scope containment;
- ownership selection;
- applicability;
- explicit task-selection validity;
- explicit write-set equality;
- Git baseline comparison;
- undeclared-write detection;
- operation-kind separation;
- contract graph structural validity.

Agentic reasoning owns semantics that cannot be mechanically established from the contract structure alone:

- whether a feature requirement implies a durable new invariant;
- how an invariant should be phrased;
- whether implementation satisfies prose intent;
- whether a dependency or interface should be redesigned;
- whether a cross-component task should be decomposed for maintainability.

The architecture should move a concern into deterministic code only when doing so does not create an unreliable second interpretation of prose semantics.

## No persisted planning boundary

Boundary does not require a feature-local `boundary.json`.

Planning and task generation may call `boundary inspect` and receive target projections, but those projections are disposable query results.

Authorization always resolves the explicitly selected canonical task scope against a fresh `ContractGraph`.

This removes:

- boundary refresh lifecycle state;
- refresh-time fingerprint sidecars;
- stale feature-boundary synchronization;
- a provider-named feature-state namespace.

## No generalized provider framework

Boundary should use concrete internal interfaces only where they simplify current code.

Do not add:

- dynamic provider registration;
- provider manifests;
- configurable semantic engines;
- runtime adapter discovery.

The native contract engine is the product implementation.

Codex and Claude skill materializers are concrete runtime integrations. Their existence demonstrates portability but does not by itself justify dynamic agent-adapter registration or a shared provider framework.

A generalized abstraction is justified only when concrete implementations demonstrate a stable shared requirement.

## Portability invariant

Replacing Spec Kit, Codex, Claude Code, or the concrete mise backend must not require redesigning:

- native contract semantics;
- target effective-context composition;
- explicit write authorization;
- task-selected implementation units;
- operation evidence;
- Git verification;
- contract-evolution separation.

Those are Boundary concepts.

Changing the distribution backend may change project tooling state and installation procedure, but must not introduce a second Boundary-owned source or dependency lock.
