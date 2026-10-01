# TODO

- [ ] Replace compatibility tests and fixtures with mise-distribution coverage.
  - Legacy Boundary-lock, source-checkout, copied-runtime, and project-launcher tests were removed with the implementation transition.
  - Add focused tests for Git source configuration, exact source identity locking, locked reinstall, upgrade to another identity, integration health/error reporting, and removal.
  - Exercise the local-Git-repository development use case separately from portable downstream project state.
  - Verify that normal downstream commands execute the mise-installed Boundary CLI rather than a copied Boundary runtime.
  - Verify that locked installation preserves exact Boundary source identity while transitive Python dependency resolution remains governed by package metadata rather than a Boundary-defined lock.
  - Verify that generated Spec Kit/runtime state remains non-canonical where still applicable.
  - Keep tests focused on Boundary-visible behavior; do not duplicate mise's own lockfile implementation.

- [ ] Finish the distribution transition and release verification.
  - Remove remaining current-architecture references to the legacy Boundary revision lock, matching source checkouts, source-checkout-driven runtime installation, and the generated project-local launcher outside historical material.
  - Update README and remaining operator/agent guidance after implementation behavior is settled.
  - Run native contract validation and the complete test suite.
  - Run the file-size check and keep changed code/documentation files below 250 lines.
  - Run a clean end-to-end downstream smoke test using the Git-backed mise model.
  - Confirm the smoke test needs only normal mise project state for Boundary version selection and creates no Boundary-specific revision or dependency lock.
  - Confirm normal agent procedure invokes the installed `boundary` executable directly.
  - Remove this TODO when all checks are green.
