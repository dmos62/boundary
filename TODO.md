# TODO

- [ ] Finish the distribution transition and release verification.
  - Remove remaining current-architecture references to the legacy Boundary revision lock, matching source checkouts, source-checkout-driven runtime installation, and the generated project-local launcher outside historical material.
  - Update README and remaining operator/agent guidance after implementation behavior is settled.
  - Run native contract validation and the complete test suite.
  - Run the file-size check and keep changed code/documentation files below 250 lines.
  - Run a clean end-to-end downstream smoke test using the Git-backed mise model.
  - Confirm the smoke test needs only normal mise project state for Boundary version selection and creates no Boundary-specific revision or dependency lock.
  - Confirm normal agent procedure invokes the installed `boundary` executable directly.
  - Remove this TODO when all checks are green.
