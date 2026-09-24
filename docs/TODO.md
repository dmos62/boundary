# Implementation TODO

Boundary's target architecture is defined in the focused `docs/spec*.md` documents.

Native contracts under `contracts/` are the only persistent Boundary contract source. Boundary authorization and verification use fresh native contract state, exact structured writes, Git baselines, atomic operation records, verified authorization epochs, and exact dirty-state carry-forward provenance.

Canonical Boundary procedure is materialized from `skills/*/SKILL.md` into concrete Codex and Claude Code discovery state. The Spec Kit integration is a change-system adapter only: structured task `Writes:` metadata is projected into native Boundary authorization at implementation entry, and actual Git writes are verified at implementation exit.

The supported downstream lifecycle, immutable lock schema, generated-source provenance, generated-state exclusions, and separated downstream/development setup are implemented.

Current verification baseline:

- native contract check passes with 15 contracts;
- Git history contains release revisions `ab7302e1d6986e0ce0db9ac8a567999e6aa3a50e` and `b43741a19ce12cc408fd493c25df17541e5a46c9`;
- `https://github.com/dmos62/speckit-specdd` is anonymously readable and both exact commit archives are anonymously downloadable;
- archive `ab7302e1d6986e0ce0db9ac8a567999e6aa3a50e` has SHA-256 `2dd4b6231e63d1c236c5d715b6852aad4ca28a77208c9248c6614ef79a0600d5`;
- archive `b43741a19ce12cc408fd493c25df17541e5a46c9` has SHA-256 `158db005bad253bd57b56cb9ea4697cbac4d29ad886248bf2ee0c05827774353`;
- release fixtures now name those published immutable revisions and exact archive checksums;
- the release-proof test remains to be confirmed against the committed real archive fixtures;
- migration-only Change Boundary, validation, verification, and workflow test suites have been removed from the active test surface;
- Spec Kit distribution tests use the current `integration/speckit*` source layout and native contracts rather than a compatibility fixture.

Work in the order below. P10 remains first priority until the committed release fixtures pass the real-archive lifecycle matrix.

## P10 — Define the reproducible downstream Boundary experience

The local checksum-verified archive lifecycle already covers fresh-clone install, health check, checksum failure, remove/reinstall, deliberate upgrade, failed-upgrade rollback, generated-state exclusions, and visible shared host registry changes.

Release-proof coverage is implemented in `tests/test_consumer_release.py` and enabled with `BOUNDARY_RELEASE_ARCHIVE_TESTS=1`.

Published identities:

- initial: `ab7302e1d6986e0ce0db9ac8a567999e6aa3a50e`;
- upgrade: `b43741a19ce12cc408fd493c25df17541e5a46c9`.

Remaining work:

- [ ] Run the fresh-clone release lifecycle matrix against the committed real archive fixtures and resolve any genuine release-path failures.

Done when:
  A fresh clone can reconstruct the same Boundary tooling and agent capabilities from the committed lock while carrying only native project contracts as persistent Boundary semantics.

## P11 — Final migration cleanup

Current documentation cleanup removed the obsolete provider bootstrap from the agent instruction surface, removed duplicate migration-era guides, and archived only concise historical context.

The compatibility-only test surface that exercised persisted Change Boundaries, legacy authority projection, the removed validation phase, legacy verification evidence, and migration workflow controls has been removed. Current distribution fixtures exercise native Boundary contracts through the Spec Kit adapter.

Remaining work:

- [ ] Remove any remaining compatibility-only production helpers, fixtures, and stale source-path terminology revealed by the supported test matrix.
- [ ] Keep all code and documentation files below 250 lines. Current known oversized implementation files include `src/boundary/authorization/record.py`, `scripts/consumer.py`, and `scripts/consumer_lock.py`; `tests/test_native_contract_cli.py` also remains above the limit.
- [ ] Run the complete supported bootstrap, native contract, authorization, adapter, packaging, and fresh-clone test matrix.

Done when:
  Current documentation describes one Boundary architecture, legacy providers survive only in explicit history if retained at all, and no downstream workflow depends on migration-era product concepts.
