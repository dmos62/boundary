# CLI help review

Existing evidence confirms that Boundary installs a `boundary` console script and exposes the intended product commands, but the available context does not contain the actual `boundary --help` output or enough CLI parser source to judge whether the top-level help is useful.

- [ ] Review the installed `boundary --help` output and focused subcommand help after a fresh development install. Check that the top-level output makes the product purpose, canonical command surface, and `authorize → implement → verify` lifecycle discoverable without requiring source inspection.
- [ ] Inspect `src/boundary/cli/`, `pyproject.toml`, applicable repository-tooling/distribution contracts, and existing CLI/distribution tests to identify how help is assembled and whether help text is tested.
- [ ] If the current help is insufficient, implement focused top-level help without changing command semantics. Prefer one authoritative CLI definition and concise argparse-native descriptions/epilog text over duplicated documentation.
- [ ] Ensure help exposes the important entrypoints: `inspect`, `authorize`, `verify`, `status`, `contracts check`, and `integration install|check|remove`, and makes explicit task selection for implementation authorization discoverable.
- [ ] Add focused regression coverage for stable help essentials rather than a brittle full-output snapshot. Cover the installed console entrypoint where practical.
- [ ] Update only documentation that is demonstrably inconsistent with the resulting CLI surface.
- [ ] Validate focused CLI/distribution tests, contract checks, the distribution suite, the full test suite, `git diff --check`, and changed-file size limits.
