---
schema: boundary.contract/v1
id: boundary-repository-tooling
owns:
  - scripts/**
---

# Repository Tooling

## Purpose

Provide reproducible Boundary development bootstrap and downstream installation from explicitly supplied Boundary source.

## Invariants

- Downstream Boundary source identity is committed as one lock containing an exact Git revision.
- Downstream lifecycle commands derive Boundary source from the repository containing the invoked consumer rather than retrieving remote source.
- Locked lifecycle operations require a clean Boundary checkout whose exact revision matches the downstream lock.
- First adoption records the current clean Boundary checkout's revision without requiring remote distribution metadata.
- Install, health-check, remove/reinstall, and deliberate upgrade operate from explicitly supplied Boundary checkouts.
- Upgrade installs the candidate before replacing the committed lock and never advances the lock after candidate installation failure.
- Generated Boundary integration state remains recreatable from matching source and is excluded locally rather than becoming downstream canonical source.
- Shared host registry and configuration files remain visible to Git rather than being hidden as Boundary-owned generated state.
- Installation and removal use supported host lifecycle mechanisms rather than patching generated state directly.
- Development bootstrap remains separate from downstream locked-source installation.
- Development bootstrap does not install or require the removed SpecDD migration provider.
- Installation failures identify missing prerequisites before relying on partially initialized generated state.

## Prohibitions

- Generated integration state must not become canonical Boundary source.
- Downstream canonical state must not contain operator-local Boundary checkout paths.
- The downstream consumer must not fetch, clone, download, or resolve Boundary releases from the project lock.
- Mutable branches, tags, or latest-release selectors must not define downstream source identity.
- Upgrade must not claim automatic rollback when the previous Boundary source checkout is unavailable.
- Legacy `.specdd/` state must not be created as part of Boundary installation.

## Interfaces

- `scripts/consumer.py` manages downstream Boundary state using the Boundary checkout that contains the invoked script.
- `scripts/install.sh` installs already materialized Boundary source for development or the downstream consumer.
