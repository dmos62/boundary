# Boundary

Boundary is a persistent-contract and operation-authorization layer for coding agents.

It separates durable project architecture from the systems used to plan changes and from the agent runtimes used to execute them.

The core relationship is:

> A change system owns feature intent and execution state. Boundary owns persistent system contracts and operation authority. Agent adapters deliver the smallest relevant procedure and effective context needed for current work.

Boundary's durable concepts are:

- persistent project contracts;
- explicit path ownership;
- additive scoped applicability;
- effective target context;
- exact implementation write scope;
- operation authorization;
- historical operation evidence;
- persistent-contract evolution;
- actual-write verification;
- progressive agent instruction disclosure;
- mise-managed downstream tool selection and installation.

These concepts are independent of any one change system or agent runtime.

## Native contracts

Canonical project contracts live under:

    contracts/**/*.contract.md

Contract location has no semantic meaning.

Each contract declares explicit ownership and applicability scopes. All matching contracts apply additively. When ownership is nested, the most-specific matching owner is primary while broader matching contracts continue to contribute constraints.

Boundary v1 deliberately avoids:

- filesystem-dependent contract meaning;
- nearest-contract-wins behavior;
- implicit directory inheritance;
- contract override or exception semantics;
- a global catch-all project contract;
- a second persistent compiled copy of project contracts.

Detailed semantics are in [docs/spec-contracts.md](docs/spec-contracts.md).

## Agent instruction model

Boundary uses progressive disclosure.

Stable procedure lives in small canonical skills:

- `boundary-scope` for planning and explicit write declaration;
- `boundary-implement` for implementation under an active authorization;
- `boundary-contracts` for deliberate persistent-contract evolution.

Operation-specific facts are queried on demand. For a target, Boundary derives ownership, applicable contracts, relevant semantic sections, dependency interfaces, and source provenance.

Project contracts are therefore loaded because they are relevant to current work rather than injected wholesale into every agent interaction.

See [docs/spec-agent-instructions.md](docs/spec-agent-instructions.md).

## Authorization model

Implementation authority comes from exact structured write declarations, not path-looking prose.

At authorization Boundary:

1. reads the current explicit write set from the change-system adapter;
2. builds the native contract graph fresh;
3. resolves ownership and effective context;
4. validates operation kind and Git starting state;
5. records one atomic operation document in current-worktree Git metadata.

Verification compares actual post-authorization Git changes with that historical evidence.

Current planning state cannot retroactively widen an operation.

See [docs/spec-authorization.md](docs/spec-authorization.md).

## Lifecycle

The mandatory implementation lifecycle is:

    authorize → implement → verify

Planning and task generation may inspect effective contract context but do not create implementation authority.

If implementation discovers another required target, the current operation must be verified and closed before a fresh write set is authorized.

Persistent-contract evolution is a separate operation and must be followed by fresh dependent implementation authorization.

See [docs/spec-lifecycle.md](docs/spec-lifecycle.md).

## Adapters

Boundary currently integrates with Spec Kit as a change-system adapter.

The adapter provides:

- active change identity;
- stable task identities;
- exact structured implementation writes;
- host-owned path classification;
- implementation entry and exit integration.

Boundary core does not depend on Spec Kit workflow terminology or feature-file structure.

Codex and Claude Code are concrete agent-runtime integrations. They materialize the same canonical Boundary skills into their respective discovery locations without changing the canonical procedure.

See [docs/spec-change-adapter.md](docs/spec-change-adapter.md) and [docs/spec-architecture.md](docs/spec-architecture.md).

## Downstream reconstruction

A downstream project commits:

- its native contracts;
- its change-system artifacts;
- its normal mise project configuration;
- `mise.lock`.

The mise configuration identifies the Boundary Git source. `mise.lock` records the exact Boundary source identity selected for locked installation.

Boundary does not define another revision lock, dependency lock, copied runtime, or project-local launcher.

Generated integration state, materialized skills, caches, provenance records, and operation evidence are not canonical project semantics.

A fresh clone reconstructs tooling through normal mise project state:

    mise install --locked
    boundary integration install
    boundary integration check

See [docs/spec-distribution.md](docs/spec-distribution.md) and [docs/setup-downstream.md](docs/setup-downstream.md).

## Development

Bootstrap the Boundary source repository with:

    mise install
    mise run bootstrap

Validate native contracts with:

    mise run contracts-check

Run the focused distribution coverage with:

    mise run test-distribution

Run the complete test suite with:

    mise run test

Additional development and test commands are documented in [docs/setup-development.md](docs/setup-development.md).

## Design documentation

The current architecture is split by responsibility:

- [docs/spec.md](docs/spec.md): product model and invariants.
- [docs/spec-architecture.md](docs/spec-architecture.md): core structures and adapter boundaries.
- [docs/spec-contracts.md](docs/spec-contracts.md): native contract format and applicability.
- [docs/spec-agent-instructions.md](docs/spec-agent-instructions.md): progressive agent instruction delivery.
- [docs/spec-authorization.md](docs/spec-authorization.md): operation evidence, Git baselines, and verification.
- [docs/spec-change-adapter.md](docs/spec-change-adapter.md): provider-neutral change-system integration.
- [docs/spec-lifecycle.md](docs/spec-lifecycle.md): authorization, implementation, verification, and contract evolution.
- [docs/spec-distribution.md](docs/spec-distribution.md): mise-managed downstream installation and source identity.
- [docs/spec-distribution-state.md](docs/spec-distribution-state.md): downstream state ownership and generated-state exclusions.
- [TODO.md](TODO.md): remaining implementation and release work.
- [docs/history/README.md](docs/history/README.md): explicitly historical migration material.

## Summary invariant

Boundary remains coherent while:

> project contracts are canonical and independently scoped; change systems provide explicit change intent; skills provide procedure; queries provide current facts; deterministic code provides authorization and verification; and downstream Boundary tooling is selected, locked, installed, and upgraded through mise using normal project tooling state.
