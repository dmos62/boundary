# Downstream Boundary Setup

This guide is for repositories that consume Boundary without carrying Boundary implementation source.

Boundary source development is documented separately in [setup-development.md](setup-development.md).

## Prerequisites

The downstream machine needs:

- Git;
- `uv`;
- Codex;
- a clean Boundary source checkout;
- the runtime required by the project's selected Spec Kit script mode.

For a project that is not yet initialized with Spec Kit, Boundary invokes the pinned Spec Kit `init` lifecycle without a `--script` override. Spec Kit 1.0.10 therefore chooses its platform default: `sh` on Linux/macOS and `ps` on Windows.

For an existing Spec Kit project, Boundary preserves the `script` value in `.specify/init-options.json`. A project selecting `"script": "ps"` must have `pwsh` available on `PATH`.

Set `BOUNDARY_SPECKIT_SCRIPT=sh|ps|py` only for an intentional script-mode transition. Boundary passes that explicit choice through Spec Kit's supported integration lifecycle and then validates the selected runtime. Without the variable, Boundary does not change an existing selection.

When the active integration is already Codex and the requested mode differs, Boundary uses Spec Kit's forced integration-upgrade lifecycle so Spec Kit itself regenerates managed scripts and integration files. This can replace intentional edits to Spec Kit-managed integration files. Commit or otherwise preserve such edits before requesting a mode transition.

The locked installer establishes the supported Spec Kit version when installation requires it.

## Canonical project state

Commit Boundary's canonical project state:

- native contracts under `contracts/`;
- the change-system artifacts your project uses;
- `boundary.lock.json`.

Do not commit generated Boundary runtime copies, installed Boundary adapter state, or materialized Boundary skills as Boundary source.

This does not mean Spec Kit project state is disposable. With pinned Spec Kit 1.0.10, keep Spec Kit persistent configuration and shareable generated state visible for normal project review. This includes `.specify/init-options.json`, `.specify/integration.json`, project extension configuration, integration manifests and registries, the active script variant, the managed `.specify/.gitignore`, and materialized core `speckit-*` skills.

The stock `.specify/.gitignore` owns Spec Kit's machine-local exclusions. Boundary does not broaden or patch that file.

The target Boundary lock has this shape:

    {
      "schema": "boundary.lock/v2",
      "source": {
        "revision": "<40-character Boundary commit>"
      }
    }

The lock records which Boundary revision the project expects. It does not contain a source URL, checksum, or local checkout path.

## First-time adoption

Choose a clean Boundary checkout at the revision the project should adopt.

Run its consumer against the downstream repository:

    python /path/to/boundary/scripts/consumer.py \
      --root /path/to/project \
      adopt

This creates `/path/to/project/boundary.lock.json` using the current Boundary checkout's exact Git revision.

Review and commit the new lock.

Boundary does not generate the project's native architectural contracts. Add and maintain those under `contracts/` as project-authored persistent semantics.

## Install locally

Using the same Boundary checkout, run:

    python /path/to/boundary/scripts/consumer.py \
      --root /path/to/project \
      install

The consumer verifies that:

- its own Boundary checkout is clean;
- its Git revision matches the project's lock.

On a new Spec Kit project, the installer lets Spec Kit choose the platform script mode. On an existing project, it validates the runtime required by the saved mode before materializing Boundary state.

It then installs generated Boundary runtime and integration state from that checkout.

No Boundary source archive is downloaded.

Review any visible Spec Kit project-state changes separately from Boundary-owned generated paths, which are locally excluded.

## Fresh clone installation

After cloning an already adopted downstream repository:

1. read the revision in `boundary.lock.json`;
2. obtain a clean Boundary checkout at that exact revision;
3. inspect any committed `.specify/init-options.json` and ensure its selected runtime is available;
4. run that checkout's consumer with `install`.

For example:

    python /path/to/matching-boundary/scripts/consumer.py \
      --root /path/to/project \
      install

The downstream repository does not need a canonical `src/boundary/`, `skills/`, `adapters/`, or `integration/` tree.

The lock intentionally does not tell Boundary where to fetch its implementation. Supplying the matching checkout is an operator responsibility.

## Recover an accidental PowerShell selection on Linux

Older Boundary revisions unconditionally passed `--script ps` to Spec Kit. A Linux project initialized by those revisions can therefore contain `"script": "ps"` even when PowerShell was never intended.

The same Spec Kit field also represents an intentional project choice, so fixed Boundary versions do not silently reinterpret an existing `ps` value. To deliberately move an affected project to shell mode, first commit or otherwise preserve intentional changes to Spec Kit-managed scripts or core integration files, then run the normal Boundary lifecycle with an explicit one-run override:

    BOUNDARY_SPECKIT_SCRIPT=sh \
      python /path/to/boundary/scripts/consumer.py \
        --root /path/to/project \
        reinstall

For an upgrade to the Boundary revision containing the fix, use the candidate checkout and `upgrade` instead:

    BOUNDARY_SPECKIT_SCRIPT=sh \
      python /path/to/new-boundary/scripts/consumer.py \
        --root /path/to/project \
        upgrade

Boundary asks Spec Kit to change the active Codex integration to `sh` with its supported `integration upgrade --force` lifecycle. The forced refresh is limited to an explicitly requested script-mode transition; normal install and check preserve the saved mode. Core scripts and generated `speckit-*` skills are regenerated by Spec Kit rather than edited by Boundary.

Spec Kit 1.0.10 can retain the previous `.specify/scripts/powershell/` directory after a `ps` to `sh` transition. That inactive directory is non-authoritative host-generated residue. `.specify/init-options.json` and the regenerated integration select the Bash implementation. Boundary leaves the old variant alone rather than deleting Spec Kit-owned files or adding mode-dependent ignore rules.

A previously tracked inactive variant may therefore remain unchanged in the repository and not appear in Git status. Its presence does not select that runtime.

Afterward, review visible Spec Kit changes, run `check`, and execute the first Spec Kit workflow step. Visible changes can include Spec Kit integration metadata, registries, active scripts, and materialized core `speckit-*` skills.

The stock `.specify/.gitignore` hides only machine-local Spec Kit state such as `.specify/feature.json` and per-machine `extensions/*/local-config.yml`. Shared `.specify/` state remains visible.

If `ps` is intentional, do not set the override; install and check will continue to require `pwsh`.

## Health check

Run from a Boundary checkout matching the project lock:

    python /path/to/boundary/scripts/consumer.py \
      --root /path/to/project \
      check

The check requires:

- the invoking Boundary checkout to match the committed lock;
- the selected Spec Kit script runtime to be available;
- installed source provenance to match the committed lock;
- generated integration state to pass that revision's health checks.

## Remove and reinstall

Remove generated Boundary integration:

    python /path/to/boundary/scripts/consumer.py \
      --root /path/to/project \
      remove

Reinstall the same locked version:

    python /path/to/boundary/scripts/consumer.py \
      --root /path/to/project \
      reinstall

Both commands must be run from a clean Boundary checkout at the locked revision.

## Deliberate upgrade

Obtain a clean Boundary checkout at the revision the project should use next.

Run that candidate checkout's consumer:

    python /path/to/new-boundary/scripts/consumer.py \
      --root /path/to/project \
      upgrade

The candidate is installed before `boundary.lock.json` is replaced.

Review and commit the resulting lock change deliberately.

If candidate installation fails, the lock remains on the previous revision. Boundary does not automatically fetch or retain the previous source, so automatic rollback is not guaranteed.

To restore the previous installation after a failed upgrade, obtain a clean Boundary checkout at the still-locked previous revision and reinstall from it.

## Generated state

Boundary maintains local Git exclusions in the worktree's Git metadata only for Boundary-owned generated integration state.

Operation authorization evidence also lives in Git metadata rather than ordinary project source.

Spec Kit owns its project configuration and shareable generated integration state. Boundary does not hide that state merely because Boundary installation caused Spec Kit to regenerate it.

Spec Kit's managed `.specify/.gitignore` remains the authority for Spec Kit machine-local exclusions. Boundary does not patch it, does not broadly ignore `.specify/`, and does not hide core `speckit-*` skills.

Boundary-owned generated files can be removed and recreated from any clean Boundary checkout at the project's locked revision.
