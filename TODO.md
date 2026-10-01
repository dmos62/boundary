# TODO

- [ ] Complete distribution release verification.
  - The canonical Spec Kit workflow overlay has been normalized to the representation Spec Kit 1.0.10 writes through `workflow overlay add`; the prior integration-check failure was caused by byte-level YAML reserialization rather than semantic overlay drift.
  - Re-run native contract validation, focused distribution coverage, and the complete test suite after the distribution-fixture and stale-test cleanup.
  - Re-run the changed-file size check and keep changed code and documentation files below 250 lines.
  - Confirm the focused mise distribution tests provide a clean Git-backed downstream smoke test using only normal mise project configuration and `mise.lock`.
  - Confirm the smoke test creates no Boundary-specific revision or dependency lock, copied runtime, or project-local launcher.
  - Confirm normal agent procedure invokes the mise-installed `boundary` executable directly.
  - Remove this TODO when all checks are green.
