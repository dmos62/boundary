# Implementation TODO

Boundary's target architecture is defined in the focused `docs/spec*.md` documents.

Native contracts under `contracts/` are the only persistent Boundary contract source. Boundary authorization and verification use fresh native contract state, exact structured writes, Git baselines, atomic operation records, verified authorization epochs, and exact dirty-state carry-forward provenance.

Canonical Boundary procedure is materialized from `skills/*/SKILL.md` into concrete Codex and Claude Code discovery state. The Spec Kit integration is a change-system adapter only: structured task `Writes:` metadata is projected into native Boundary authorization at implementation entry, and actual Git writes are verified at implementation exit.

The supported downstream lifecycle, immutable lock schema, generated-source provenance, generated-state exclusions, and separated downstream/development setup are implemented.

Current verification baseline:

- native contract check passes with 15 contracts;
- Git history contains published release revisions `ab7302e1d6986e0ce0db9ac8a567999e6aa3a50e` and `b43741a19ce12cc408fd493c25df17541e5a46c9`;
- both exact GitHub commit archives are anonymously downloadable and match the committed release-fixture SHA-256 values;
- the real-archive fresh-clone lifecycle proof passes for install, health check, remove/reinstall, deliberate upgrade, failed checksum upgrade rollback, generated-state exclusions, and visible shared host state;
- migration-only SpecDD source-adjacent `.sdd` material surfaced outside explicit history has been removed from the active source and fixture surface;
- known source, test, and documentation files are kept at or below 250 lines by separating operation-record serialization, consumer state handling, and native CLI test support.

## P11 — Final migration cleanup

Remaining work:

- [ ] Run the complete supported bootstrap, native contract, authorization, adapter, packaging, and fresh-clone test matrix after the cleanup refactors.
  - The latest harness run passed the native contract check and all 89 enabled unit/integration tests; two published-archive tests were skipped because release-archive proof was not enabled.
  - The bootstrap health check was run against an unprepared worktree and correctly reported that the Boundary Spec Kit adapter was not installed. The verification harness now runs development bootstrap before the health check.
  - The verification harness now explicitly enables the published immutable-archive lifecycle proof after the ordinary test suite.
  - If the updated verification sequence passes, delete this remaining P11 item.

Done when:
  Current documentation describes one Boundary architecture, legacy providers survive only in explicit history if retained at all, and no downstream workflow depends on migration-era product concepts.
