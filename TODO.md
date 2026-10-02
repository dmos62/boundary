# Boundary version self-reporting

Boundary now exposes top-level version reporting from the installed `boundary-cli` distribution metadata. No package-level version constant was added; Git-derived package metadata remains the sole version authority. Distribution semantics are documented in `docs/spec-distribution.md`, without duplicating setup instructions.

- [ ] Re-run the complete validation set after the focused distribution test was made insensitive to argparse help-line wrapping: contract checks, focused CLI/distribution tests, the distribution suite, the complete test suite, fresh installed `boundary --help` / `boundary --version` output, `git diff --check`, changed-file size checks, and final Git status. The only observed test failure was the exact unwrapped `--version` help assertion; implementation output itself was correct. If validation passes, remove this completed TODO so the file is empty.
