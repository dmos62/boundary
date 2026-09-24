# Implementation TODO

Boundary's target architecture is defined in the focused `docs/spec*.md` documents.

Native contracts under `contracts/` are the only persistent Boundary contract source. Boundary authorization and verification use fresh native contract state, exact structured writes, Git baselines, atomic operation records, verified authorization epochs, and exact dirty-state carry-forward provenance.

Canonical Boundary procedure is materialized from `skills/*/SKILL.md` into concrete Codex and Claude Code discovery state. The Spec Kit integration is a change-system adapter only: structured task `Writes:` metadata is projected into native Boundary authorization at implementation entry, and actual Git writes are verified at implementation exit.

The supported downstream lifecycle, immutable lock schema, generated-source provenance, generated-state exclusions, and separated downstream/development setup are implemented.

Current verification baseline:

- native contract check passes with 15 contracts;
- consumer tests pass with 10 tests, of which the two published-archive tests are skipped;
- the release proof remains unavailable because two suitable published immutable Boundary revisions have not yet been established;
- active documentation now describes the native Boundary architecture only, while concise migration history is isolated under `docs/history/`.

Work in the order below. P10 remains first priority, but its remaining work is externally publication-blocked; see `HUMAN-REQUEST.md`. While that evidence is unavailable, continue P11 cleanup that does not alter release-proof semantics. Return to P10 as soon as the release-candidate harness reports two usable archives.

## P10 — Define the reproducible downstream Boundary experience

The local checksum-verified archive lifecycle already covers fresh-clone install, health check, checksum failure, remove/reinstall, deliberate upgrade, failed-upgrade rollback, generated-state exclusions, and visible shared host registry changes.

Release-proof coverage is implemented in `tests/test_consumer_release.py` and enabled with `BOUNDARY_RELEASE_ARCHIVE_TESTS=1`.

Remaining work:

- [ ] Commit `tests/fixtures/consumer-release/boundary.lock.json` and `boundary-upgrade.lock.json` using two distinct, publicly retrievable immutable Boundary commit archives and their exact SHA-256 values.
- [ ] Run the fresh-clone release lifecycle matrix against those committed real archive fixtures.
- [ ] Delete `HUMAN-REQUEST.md` after the two published archive identities are established and verified.

`dev-scripts.include` fetches published refs and reports release candidates. A candidate is usable only when the required downstream source and release-proof implementation are present and the exact anonymous GitHub commit archive can be downloaded and checksummed.

Do not substitute unpublished revisions, mutable branch or tag archives, authenticated-only downloads, synthetic archives, or fabricated checksums.

Done when:
  A fresh clone can reconstruct the same Boundary tooling and agent capabilities from the committed lock while carrying only native project contracts as persistent Boundary semantics.

## P11 — Final migration cleanup

Current documentation cleanup removed the obsolete provider bootstrap from the agent instruction surface, removed duplicate migration-era guides, and archived only concise historical context.

Remaining work:

- [ ] Remove compatibility-only tests/helpers and shrink `files.include` again after that cleanup. The obsolete native-contract migration test that imported the removed compatibility adapter has already been deleted.
- [ ] Keep all canonical code and documentation files below 250 lines.
- [ ] Run the complete supported bootstrap, native contract, authorization, adapter, packaging, and fresh-clone test matrix.

Done when:
  Current documentation describes one Boundary architecture, legacy providers survive only in explicit history if retained at all, and no downstream workflow depends on migration-era product concepts.
