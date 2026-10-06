# Downstream Boundary Setup

This guide is for repositories that consume Boundary without carrying Boundary implementation source.

Boundary source development is documented separately in [setup-development.md](setup-development.md).

## Prerequisites

The downstream machine needs:

- Git;
- write access to the current worktree's Git metadata location so Boundary can automatically probe and persist operation evidence under `<git-dir>/boundary` at authorization and verification entry;
- mise;
- Codex when using the current Codex runtime integration;
- the runtime required by the project's selected Spec Kit script mode.

The current Spec Kit adapter requires Spec Kit 1.0.10. The recommended project configuration lets mise install both Boundary and the pinned Spec Kit CLI.

A separate operator-supplied Boundary checkout is not required for normal downstream use.

## Project tooling state

Commit the project's normal `mise.toml` and `mise.lock`.

The approved Boundary tool selector is the mise `pipx:` Git-source form. Git-source installs use top-level source-identity locking rather than a native frozen Python dependency sidecar.

A typical project declaration is:

    [tools]
    python = "3.12"
    uv = "latest"
    "pipx:git+https://github.com/specdd/speckit-boundary.git" = { version = "latest", depends = ["python", "uv"] }
    "pipx:git+https://github.com/github/spec-kit.git" = { version = "v1.0.10", depends = ["python", "uv"] }

The Boundary Git repository locator is stable project configuration. `mise.lock` records the exact Boundary source identity selected from that locator.

These are normal project/tooling files owned through mise. They are not Boundary persistent contracts.

Boundary defines no additional project-local revision or dependency lock.

Portable project state must not depend on an operator-local Boundary checkout path.

## Boundary persistent semantics

Commit Boundary's persistent project semantics:

- native contracts under `contracts/`;
- the change-system artifacts your project uses.

Do not commit generated Boundary integration state as Boundary source.

This does not mean Spec Kit project state is disposable.

With pinned Spec Kit 1.0.10, keep Spec Kit persistent configuration and shareable generated state visible for normal project review.

This includes `.specify/init-options.json`, `.specify/integration.json`, project extension configuration, integration manifests and registries, the active script variant, the managed `.specify/.gitignore`, and materialized core `speckit-*` skills.

The stock `.specify/.gitignore` owns Spec Kit's machine-local exclusions. Boundary does not broaden or patch that file.

## First-time adoption

Add the approved Git-backed Boundary tool declaration to the project's mise configuration.

Then create or update mise's lock state and install from it:

    mise lock
    mise install --locked

After the installed `boundary` executable is available, materialize Boundary-owned project integration:

    boundary integration install

Review visible host-owned project-state changes separately from Boundary-owned generated paths.

Boundary does not generate the project's native architectural contracts. Add and maintain those under `contracts/` as project-authored persistent semantics.

Adoption creates no Boundary-specific revision lock, copied Boundary runtime, install-provenance document, or project-local Boundary launcher.

## Fresh clone installation

After cloning an already configured downstream repository:

    mise install --locked
    boundary integration install
    boundary integration check

The committed mise lock selects the exact Boundary source identity.

The project does not need a canonical `src/boundary/`, `skills/`, `adapters/`, or `integration/` source tree copied from Boundary.

The project also does not need a separate Boundary checkout matching an independently maintained pin.

## Dependency reproducibility

Locked installation reproduces the selected Boundary Git source identity.

Boundary does not require mise to freeze the complete transitive Python dependency graph for the Git-backed tool.

The approved `pipx:` Git-source installation remains version/source locked while Boundary package metadata defines supported dependency constraints and the installer resolves compatible dependencies.

A later installation of the same Boundary source may therefore select a newer compatible transitive dependency.

That is part of the approved distribution model.

Projects that impose broader environment-reproduction policy may do so independently, but Boundary does not add a second lock or dependency sidecar of its own.

## Normal Boundary commands

Use the installed CLI directly:

    boundary inspect <target...>
    boundary authorize <task-id> [<task-id> ...]
    boundary verify
    boundary status
    boundary contracts check

Normal procedure must not require callers to provide Python import paths, invoke Boundary as a Python module, choose a uv cache directory, locate adapter scripts, or execute a generated project-local launcher.

## Spec Kit script mode

For a project that is not yet initialized with Spec Kit, Boundary invokes the pinned Spec Kit lifecycle without forcing a script mode unless explicitly requested.

Spec Kit 1.0.10 therefore chooses its platform default.

For an existing Spec Kit project, Boundary preserves the `script` value in `.specify/init-options.json`.

A project selecting `"script": "ps"` must have `pwsh` available on `PATH`.

Set:

    BOUNDARY_SPECKIT_SCRIPT=sh|ps|py boundary integration install

only for an intentional script-mode transition.

Boundary passes that explicit choice through Spec Kit's supported lifecycle and then validates the selected runtime.

When the active integration is already Codex and the requested mode differs, Boundary uses Spec Kit's supported forced integration-upgrade lifecycle so Spec Kit itself regenerates managed scripts and integration files.

Commit or otherwise preserve intentional edits to Spec Kit-managed integration files before requesting such a transition.

## Recover an accidental PowerShell selection on Linux

Older integration state may select `"script": "ps"` on Linux even when PowerShell was not intended.

Because the same field can represent an intentional project choice, Boundary must not silently reinterpret it.

To deliberately move the project to shell mode, preserve intentional host-managed changes and run:

    BOUNDARY_SPECKIT_SCRIPT=sh boundary integration install

Boundary asks Spec Kit to perform the supported mode transition.

Core scripts and generated `speckit-*` skills are regenerated by Spec Kit rather than edited directly by Boundary.

Spec Kit may retain the previous PowerShell script directory after the transition.

That inactive directory is non-authoritative host-generated residue.

`.specify/init-options.json` and the regenerated active integration determine execution.

Boundary leaves the old variant alone rather than deleting Spec Kit-owned files or adding mode-dependent ignore rules.

## Integration health check

Run:

    boundary integration check

The check validates Boundary-owned integration state and applicable host prerequisites, including the selected Spec Kit script runtime.

It also rejects stale copied-runtime or project-launcher state left by the retired distribution model.

It does not compare the running Boundary executable with a second Boundary-owned source pin.

Mise remains authoritative for installation from committed mise state.

## Upgrade

Change the desired Boundary source selector in the project's mise configuration when necessary.

Then re-resolve only the Boundary selection and install from the resulting mise lock:

    mise lock --bump 'pipx:git+https://github.com/specdd/speckit-boundary.git'
    mise install --locked
    boundary integration install
    boundary integration check

Review the mise state change deliberately.

Boundary does not keep a second revision pin or promise an independent rollback mechanism.

If an upgrade needs to be reverted, restore the prior mise configuration and lock state through the project's normal version-control/tooling workflow and reinstall it.

## Remove

First remove Boundary-owned generated integration state:

    boundary integration remove

Then remove the Boundary Git tool declaration from the project's mise configuration and update mise lock state through supported mise commands.

Remove the Spec Kit declaration only if the project no longer uses Spec Kit independently.

Removal must not delete host-owned persistent configuration or shareable generated state.

## Generated state

Boundary maintains local Git exclusions only for Boundary-owned generated integration state.

Operation authorization evidence also lives in Git metadata rather than ordinary project source.

Spec Kit owns its project configuration and shareable generated integration state.

Boundary does not hide that state merely because Boundary integration caused Spec Kit to regenerate it.

Spec Kit's managed `.specify/.gitignore` remains the authority for Spec Kit machine-local exclusions.

Boundary does not patch it, does not broadly ignore `.specify/`, and does not hide core `speckit-*` skills.

Boundary-owned generated integration files can be removed and recreated by the installed Boundary CLI.
