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

Spec Kit records its selected script mode in `.specify/init-options.json`.
Boundary preserves that project choice rather than silently changing it. In
particular, a project selecting `"script": "ps"` must have `pwsh` available on
`PATH`.

The Boundary installer validates the selected script runtime before modifying
generated Boundary integration state, so an unavailable PowerShell runtime is
reported during installation or health checking rather than during the first
Spec Kit workflow command.

The locked installer establishes the supported Spec Kit version when installation requires it.

## Canonical project state

Commit:

- native contracts under `contracts/`;
- the change-system artifacts your project uses;
- `boundary.lock.json`.

Do not commit generated Boundary runtime copies, installed adapter state, or materialized Boundary skills as Boundary source.

The target lock has this shape:

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

The installer also validates the runtime required by the existing Spec Kit
script selection before materializing Boundary state.

It then installs generated Boundary runtime and integration state from that checkout.

No Boundary source archive is downloaded.

## Fresh clone installation

After cloning an already adopted downstream repository:

1. read the revision in `boundary.lock.json`;
2. obtain a clean Boundary checkout at that exact revision;
3. ensure the runtime selected by `.specify/init-options.json` is available;
4. run that checkout's consumer with `install`.

For example:

    python /path/to/matching-boundary/scripts/consumer.py \
      --root /path/to/project \
      install

The downstream repository does not need a canonical `src/boundary/`, `skills/`, `adapters/`, or `integration/` tree.

The lock intentionally does not tell Boundary where to fetch its implementation. Supplying the matching checkout is an operator responsibility.

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

Boundary maintains local Git exclusions in the worktree's Git metadata for Boundary-owned generated integration state.

Operation authorization evidence also lives in Git metadata rather than ordinary project source.

Shared Spec Kit registry or configuration files are not automatically ignored by Boundary. If installation changes shared host state, that change remains visible in Git status and should be handled according to the project's Spec Kit configuration policy.

Boundary-owned generated files can be removed and recreated from any clean Boundary checkout at the project's locked revision.
