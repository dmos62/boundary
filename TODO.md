# TODO

- [ ] Replace the custom `boundary.lock.json` / source-checkout distribution model with mise-managed Boundary installation and locking.
  - Treat this as a distribution-architecture change, not a compatibility patch.
  - The target model is that the downstream project uses mise to install Boundary and `mise.lock` to retain the resolved Boundary revision and Python dependency resolution. Boundary must not maintain a second revision lock.
  - Investigation is still active. The supplied harness currently reports mise 2026.9.12. Keep findings and rejected mechanisms in `DEBUGGING.md` until the exact workflow is proven.
  - First prove the exact mise mechanism before making it normative:
    - install Boundary as a real `boundary` CLI from a local Boundary Git repository;
    - select an exact commit that exists in that repository rather than implicitly using its current working-tree `HEAD`;
    - generate/update `mise.lock`;
    - reproduce the installation with `mise install --locked`;
    - confirm that an unavailable revision and incomplete lock fail closed;
    - confirm whether dirty state or a different checked-out `HEAD` in the source repository can affect the selected committed revision;
    - establish the minimum supported mise/uv behavior needed for the workflow.
  - Local Git source support is a required use case. Do not standardize undocumented `pypi:git+file://...` syntax without proving it against the supported mise version. If mise cannot robustly lock/install that form, choose another mise-native mechanism rather than recreating a Boundary revision lock or exposing raw `uv` as the consumer interface.
  - Keep operator-local filesystem paths out of portable committed project state. Determine how the local Boundary source repository is supplied to mise without making an absolute source path canonical project semantics.
  - Reject a mechanism that only pins the top-level Git revision if it cannot also satisfy the required Python dependency-resolution locking model.

- [ ] Rewrite the distribution specifications around the proven mise model.
  - Remove `boundary.lock.json` from Boundary-defined canonical downstream state.
  - Remove the `boundary.lock/v*` format and all requirements to create, read, validate, migrate, or update it.
  - Remove the invariant that an operator-supplied Boundary checkout must be clean and have `HEAD` exactly equal to a committed Boundary lock.
  - Remove the requirement that downstream lifecycle commands themselves compare a supplied checkout revision with a Boundary-owned pin.
  - Define `mise.toml`/the applicable mise configuration and `mise.lock` ownership explicitly. They are normal project/tooling state managed through mise rather than a second Boundary contract format.
  - Define how a requested Boundary revision enters mise configuration, how `mise lock` records it, and how `mise install --locked` reproduces it.
  - Define the role of an operator-local source repository separately from portable project state.
  - Rework adoption, installation, health checking, upgrade, and removal semantics so revision selection and locking belong to mise.
  - Specify whether Boundary still needs any generated project-local launcher. Prefer the installed `boundary` executable directly unless a launcher has a remaining semantic responsibility unrelated to locating Python/runtime packages.
  - Preserve the distinction between generated integration state and persistent project contracts.
  - Keep historical documentation historical; do not preserve obsolete lock behavior merely for migration compatibility.
  - Update `docs/spec.md`, focused distribution/state/architecture/lifecycle specs, setup documentation, and applicable native contracts together so the model is orthogonal and consistent.

- [ ] Make Boundary a conventional mise-installable CLI and delete the old lock/check-out mechanics.
  - Ensure the Boundary source repository has the packaging metadata/console entry point required for mise's Python-tool installation to expose `boundary`.
  - Remove production code whose purpose is reading, writing, validating, comparing, or upgrading `boundary.lock.json`.
  - Remove source-checkout cleanliness/revision matching code that exists only to enforce the old distribution invariant.
  - Remove obsolete install provenance or generated launcher/runtime machinery when mise now owns that responsibility; retain integration materialization only where it still has an independent purpose.
  - Simplify lifecycle commands rather than wrapping obsolete mechanics in new names.
  - Make normal downstream procedure use semantic commands such as `boundary status`, `boundary inspect`, and `boundary contracts check`, with no `PYTHONPATH`, `python -m boundary`, or direct `uv` knowledge.
  - Keep Boundary's own repository-development workflow behind mise tasks as well, so development and consumer instructions do not repeat Python environment plumbing.
  - After the specification pass identifies the implementation paths, update `files.include` to expose only those implementation files and their focused tests for the next iteration.

- [ ] Replace compatibility tests and fixtures with mise-distribution coverage.
  - Delete tests whose only asserted behavior is the existence or semantics of `boundary.lock.json`.
  - Add focused tests for configuration generation/update, exact revision selection, locked reinstall, upgrade to another revision, health/error reporting, and removal.
  - Exercise the local-Git-repository use case explicitly.
  - Verify that normal downstream commands execute the mise-installed Boundary CLI rather than a copied Boundary runtime.
  - Verify that generated Spec Kit/runtime state remains non-canonical where still applicable.
  - Keep tests focused on Boundary-visible behavior; do not duplicate mise's own lockfile implementation.

- [ ] Finish the distribution transition and release verification.
  - Remove remaining current-architecture references to `boundary.lock.json`, matching source checkouts, and source-checkout-driven runtime installation outside historical material.
  - Update README/setup/operator guidance after implementation behavior is settled.
  - Run native contract validation and the complete test suite.
  - Run the file-size check and keep changed code/documentation files below 250 lines.
  - Run a clean end-to-end downstream smoke test: provide a local Boundary repository plus exact revision, let mise lock/install it, invoke the installed `boundary`, upgrade the requested revision through mise, reinstall in locked mode, and confirm no Boundary-specific revision lock is created.
  - Remove this TODO when all checks are green.
