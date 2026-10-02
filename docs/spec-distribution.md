# Downstream Distribution and Installation

Boundary is distributed downstream as a conventional Git-backed Python CLI installed through mise.

Mise owns Boundary version selection and installation. Boundary owns Boundary-specific project integration and runtime semantics.

Downstream project-state ownership and generated-state exclusion are defined separately in [spec-distribution-state.md](spec-distribution-state.md).

## Distribution guarantees

The downstream distribution model requires:

- a stable Git source locator for Boundary;
- an exact Boundary Git source identity in locked mise state;
- portable committed mise configuration and lock state;
- an installed `boundary` console entry point;
- no Boundary-specific revision or dependency lock;
- no operator-local source path in portable project state.

The complete transitive Python dependency graph is not part of Boundary's downstream locking guarantee.

Boundary package metadata defines compatible Python dependencies. The installation backend selected by mise resolves those dependencies when installing the locked Boundary source.

This intentionally distinguishes exact Boundary source identity from complete Python-environment reproduction.

## Mise-owned project state

Boundary distribution uses normal mise project state.

The applicable mise configuration records the Boundary Git source and tool selection.

`mise.lock` records the exact source identity selected by mise for locked installation.

These files are project/tooling state owned through mise. They are not Boundary persistent contracts and Boundary does not define an additional lock format beside them.

Boundary must not duplicate mise state into another revision pin, dependency lock, install-provenance document, or copied runtime manifest.

## Git source identity

The configured Boundary source must be portable for the intended consumers.

A stable repository locator may be committed in mise configuration.

An operator-local checkout path must not be required by portable downstream state.

The configuration may use a source selector supported by the chosen mise backend. Locked installation authority comes from the exact source identity recorded by mise rather than from the mutability of a branch or tag selector.

Updating the selected Boundary source identity is a mise lock transition.

## Dependency policy

Boundary does not require mise to persist a native frozen uv graph for the Git-backed installation.

Runtime dependency compatibility is instead part of Boundary's Python package metadata and release/test discipline.

A later installation of the same Boundary source may therefore resolve a newer compatible transitive dependency when the declared constraints permit it.

That behavior is accepted by the downstream distribution contract.

Projects that require complete environment reproduction may impose broader environment-management policy of their own, but Boundary does not create a second project-local dependency lock for itself.

## Boundary package and executable

Boundary source must be a conventional installable Python package.

Its package metadata must expose one console entry point:

    boundary

The installed executable is the canonical downstream command surface.

Boundary's Python package version is derived from Git through the package build configuration. The top-level command:

    boundary --version

reports the version from the installed `boundary-cli` distribution metadata. Boundary source modules and documentation must not introduce a separate authoritative version constant.

Normal downstream procedure uses commands such as:

    boundary inspect <target...>
    boundary authorize --task <task-id>
    boundary verify
    boundary status
    boundary contracts check

Callers do not provide `PYTHONPATH`, invoke Boundary through `python -m`, know adapter script paths, choose a uv cache directory, or locate copied Boundary source.

A project-local launcher must not be generated merely to locate Boundary's Python runtime.

## Project integration

Tool installation and Boundary project integration are separate responsibilities.

Mise installs the Boundary executable.

Boundary then materializes or updates Boundary-owned integration state through the installed CLI:

    boundary integration install

That operation may invoke supported host lifecycle mechanisms to materialize change-system and agent-runtime integration state.

It does not select or lock the Boundary version.

Generated integration state remains recreatable and non-canonical where defined by [spec-distribution-state.md](spec-distribution-state.md).

## First-time adoption

A project adopts Boundary distribution by configuring the desired Git-backed Boundary tool in mise project configuration.

The operator then creates or updates mise's lock state and performs a locked installation using supported mise commands.

Conceptually:

    configure Boundary Git source in mise project state
    mise lock
    mise install --locked
    boundary integration install

Adoption does not create a Boundary-specific source pin.

Adoption does not infer or generate native architectural contracts. Native contracts remain project-authored persistent semantics.

## Fresh clone setup

A fresh clone uses committed mise project state.

The normal sequence is:

    mise install --locked
    boundary integration install

No separate Boundary checkout is required.

No Boundary source revision is read from a Boundary-owned lock.

No source tree is copied into the project merely to make the CLI executable.

If the configured Git source is unavailable, locked installation fails as an external distribution prerequisite rather than falling back to an operator-local checkout.

## Integration health checking

Boundary validates the state it owns through:

    boundary integration check

Integration checking verifies applicable concerns such as:

- required host runtimes;
- generated Boundary integration state;
- materialized Boundary skills;
- configured change-system integration;
- Boundary-owned generated-state exclusions;
- compatibility of generated integration state with the running Boundary CLI.

It does not duplicate mise's source-lock verification.

Whether the requested Boundary tool source can be installed under the committed mise lock is mise's responsibility.

`boundary status` remains the authorization-state query defined by the lifecycle specification and is not overloaded with distribution health semantics.

## Upgrade behavior

A Boundary upgrade changes mise-managed tool selection.

The operator changes the desired Boundary source selector when necessary, asks mise to re-resolve the relevant fuzzy selection, and installs from the resulting lock.

Conceptually:

    update Boundary selection in mise project state when necessary
    mise lock --bump <Boundary tool>
    mise install --locked
    boundary integration install
    boundary integration check

The mise lock transition is authoritative for the selected Boundary source identity.

Boundary does not maintain an old source pin for rollback.

If the upgraded Boundary integration fails, the project may restore prior mise configuration and lock state through normal version-control or tooling procedures and reinstall that state.

Boundary must not claim rollback guarantees beyond what the project's mise and version-control state provide.

## Removal

Boundary-owned generated integration state is removed through:

    boundary integration remove

Removing the tool itself is a mise configuration operation.

A complete removal therefore consists of:

- removing Boundary-owned integration state;
- removing the Boundary tool declaration from mise project configuration;
- updating mise lock state through supported mise procedure.

Removal must not delete host-owned persistent configuration or shareable generated state merely because Boundary previously caused that state to be generated.

## Operator-local source repositories

A local Boundary checkout remains useful for Boundary development, testing, and preparing commits.

It is not part of the portable downstream distribution contract.

Downstream configuration must not depend on the checkout's filesystem path.

A local repository may be used in focused development or test fixtures when explicitly testing local source behavior, but such a path must not become ordinary committed consumer state.

## Development installation

Boundary source development uses repository-owned mise configuration and tasks.

Development commands should expose the same installed CLI surface used by consumers instead of teaching contributors private Python module invocation.

Repository tasks may bootstrap editable/local development state, run tests, validate contracts, and exercise integrations.

Development convenience does not redefine downstream distribution semantics.

## Failure behavior

Distribution or integration work fails clearly when:

- mise project configuration for Boundary is missing or invalid;
- the configured Git source cannot be reached when installation requires it;
- locked installation cannot reproduce the exact Boundary source identity recorded by mise;
- Boundary package metadata cannot produce an executable `boundary` command;
- required host runtimes are unavailable;
- generated Boundary integration state is incomplete or stale;
- integration removal cannot distinguish Boundary-owned state from host-owned state.

Failure must not cause Boundary to create an alternate revision lock, dependency lock, local checkout pin, or hidden package-management path.

## Source and package boundary

Boundary deliberately relies on mise for tool source selection and installation.

Boundary package metadata owns Python compatibility constraints.

Boundary integration code owns generated project integration.

These responsibilities remain separate:

> mise selects and installs Boundary; the installed Boundary CLI manages Boundary-specific project integration; Boundary contracts and authorization semantics remain independent of both.
