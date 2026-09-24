# Downstream Distribution and Installation

Boundary downstream installation is driven by an operator-supplied Boundary source checkout whose exact Git revision is recorded by the consumer project.

Boundary does not fetch its own source or require a downstream repository to encode a remote distribution location.

## Canonical downstream state

Boundary-specific downstream canonical state is limited to:

- native project contracts under `contracts/`;
- change-system artifacts that describe active product work;
- `boundary.lock.json`.

Installed runtime copies, extensions, presets, workflow overlays, materialized agent skills, caches, install provenance, and operation evidence are not canonical project semantics.

## Boundary lock

The target downstream lock uses schema `boundary.lock/v2`.

Its source record contains exactly:

- `revision`: the exact 40-character Git commit identity of the Boundary source adopted by the project.

A lock has this shape:

    {
      "schema": "boundary.lock/v2",
      "source": {
        "revision": "<40-character Boundary commit>"
      }
    }

The lock records source identity only.

It does not contain:

- a GitHub archive URL;
- an archive checksum;
- a branch or tag;
- an operator-local checkout path;
- generated integration configuration.

The lock is therefore not sufficient to retrieve Boundary source. The operator or surrounding development environment is responsible for supplying a Boundary checkout at the recorded revision.

## Source checkout

Downstream lifecycle commands run from the Boundary repository containing the invoked `scripts/consumer.py`.

The consumer derives its source root from its own location and validates that source as a Git checkout.

Except during first adoption or deliberate upgrade, the source checkout must:

- be at an exact Git commit;
- be clean;
- have a revision equal to `boundary.lock.json`.

A dirty checkout is not accepted for downstream lifecycle work because the bytes being installed would no longer be identified solely by the recorded revision.

Operator-local checkout paths never become downstream canonical state.

Boundary does not fetch, clone, download, or otherwise discover a matching checkout automatically.

## Adoption

A project adopts Boundary by running the consumer from the clean Boundary checkout it intends to use:

    python /path/to/boundary/scripts/consumer.py \
      --root /path/to/project \
      adopt

Adoption:

1. validates the Boundary source checkout;
2. requires that the downstream project does not already have a Boundary lock;
3. writes `boundary.lock.json` with the checkout's exact revision.

Adoption changes canonical project state.

It does not infer or generate project architectural contracts. Native contracts remain project-authored persistent semantics.

Adoption and local installation remain separate operations so that creating canonical project configuration is distinct from materializing disposable local state.

## Installation

After adoption, or in a fresh clone of an already adopted project, installation is run from a clean Boundary checkout at the locked revision:

    python /path/to/boundary/scripts/consumer.py \
      --root /path/to/project \
      install

Installation:

1. validates the consumer's own Boundary source checkout;
2. requires its revision to equal the committed lock;
3. delegates installation to `scripts/install.sh` from that checkout;
4. records generated installation provenance;
5. maintains local Git exclusions for Boundary-owned generated state.

No Boundary source archive is downloaded or extracted.

The generated runtime therefore comes directly from the exact checkout whose revision is recorded by the project.

## Fresh clone setup

A fresh downstream clone does not reconstruct Boundary source from `boundary.lock.json`.

The operator first obtains a Boundary checkout at the revision named by the lock, using whatever source-management process is appropriate for the environment.

The operator then runs that checkout's consumer against the downstream project.

This external source-supply requirement is intentional. Boundary's downstream lock pins source identity without also acting as a package registry or source-distribution protocol.

## Generated-state exclusion

Boundary-owned generated integration state is kept out of normal downstream Git status through a managed block in the current worktree's Git `info/exclude`.

This avoids making project `.gitignore` part of Boundary's canonical installation semantics.

The managed exclusions cover:

- materialized Boundary skills;
- generated change-system Boundary command skills;
- installed Boundary runtime source;
- the Boundary extension;
- the Boundary preset;
- the Boundary workflow overlay.

Change-system feature artifacts are not broadly ignored.

Shared host registry and configuration files are not hidden merely because Boundary installation changes them. Those paths remain visible in Git status and are handled according to the host system's own project-state policy.

Clean-consumer coverage therefore distinguishes Boundary-owned generated paths from shared host state: Boundary-owned generated paths must not appear in Git status after installation, while any shared host registry delta remains explicit and reviewable.

## Lifecycle commands

The downstream consumer supports six explicit lifecycle operations.

`adopt` records the current clean Boundary checkout's revision as the project's initial source pin.

`install` materializes generated state from a checkout matching the committed lock.

`check` confirms source-checkout identity, installed provenance, generated-state exclusions, and the health checks supplied by that Boundary revision.

`remove` removes the installed Boundary integration and its managed local exclusions using a checkout matching the committed lock.

`reinstall` removes and materializes the same locked version using a matching checkout.

`upgrade` is run from the clean candidate Boundary checkout. It validates and installs that candidate before replacing the committed lock with the candidate revision.

No lifecycle operation fetches a remote release or follows a branch, tag, or latest-release selector.

## Upgrade behavior

A deliberate upgrade is initiated from the Boundary checkout that should become the new project pin:

    python /path/to/new-boundary/scripts/consumer.py \
      --root /path/to/project \
      upgrade

The candidate checkout must be clean and must differ from the currently locked revision.

The upgrade:

1. reads the existing lock;
2. validates the candidate checkout;
3. installs the candidate source;
4. replaces the lock only after candidate installation succeeds;
5. records generated provenance for the new revision.

If candidate installation fails, the committed lock remains unchanged.

Because Boundary does not retrieve or retain old source distributions, upgrade does not promise automatic restoration of the previous installation. A failed candidate may leave local generated or shared host state requiring repair.

Restoring the previous installation requires a Boundary checkout at the still-locked previous revision followed by `reinstall` or `install`, as appropriate.

The lock therefore remains authoritative even when local upgrade work fails.

## Health checking

`check` first verifies that the invoking Boundary checkout matches the project lock.

It then verifies that generated installation provenance names the same revision and runs the health checks supplied by that checkout.

A checkout at a different revision cannot be used to declare a locked installation healthy.

## Development installation

Boundary source development continues to use `scripts/bootstrap.sh` or `scripts/install.sh --source <local-source>`.

Development installation is distinct from downstream locked-source lifecycle operations.

The source installer may accept already materialized local source directories or local archives for development purposes. Those inputs do not define downstream distribution semantics.

## Failure behavior

Downstream lifecycle work fails before installation when:

- the lock schema is malformed;
- the lock revision is malformed;
- the invoking Boundary checkout cannot be identified;
- the invoking Boundary checkout is dirty;
- a locked lifecycle command is run from a checkout at a different revision;
- adoption is attempted when a lock already exists;
- upgrade is attempted from the already locked revision.

The installer then fails when that Boundary revision's required source or local host prerequisites are incomplete.

Health checking fails when installed provenance no longer equals the committed lock or when generated integration state is incomplete.

Upgrade failure does not advance the lock.

## Source-supply boundary

Boundary deliberately does not define how operators obtain the required source checkout.

That responsibility may be satisfied by a developer clone, a monorepo toolchain checkout, a package prepared by an organization, a CI cache, or another source-management process.

Those mechanisms are outside Boundary's downstream canonical state.

The downstream contract is only:

> use a clean Boundary checkout at the exact revision recorded by the project.
