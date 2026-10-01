# TODO

- [ ] Decide which distribution requirement changes after the mise-native incompatibility.
  - The ordinary-PyPI source bridge is now rejected on observed runtime evidence under mise 2026.9.12 and uv 0.12.17.
  - `mise lock --upgrade` succeeded for an exact commit-derived Boundary package version and created mise's native uv dependency sidecar with a nontrivial Python dependency graph.
  - The resulting `uv.lock` persisted the disposable registry URL and concrete wheel URLs under `http://127.0.0.1:<ephemeral-port>/...`.
  - The committed lock state therefore cannot be portable while the package service remains operator-local and disposable.
  - The project state did not contain the operator's Boundary source path, and unavailable package/revision identity plus incomplete `mise.lock` both failed closed.
  - The subsequent locked-install probe encountered an isolated-state Python shim problem, but that no longer blocks the architecture decision: persistence of the disposable service locator already violates a required acceptance criterion.
  - The alternative mise Git-backed Python path preserves source identity but does not provide the native frozen Python dependency graph required by the current target.
  - No tested mise-native Python distribution family satisfies the complete current requirement set.
  - Do not hide the incompatibility behind `boundary.lock.json`, another Boundary-owned dependency/revision lock, raw `uv` consumer procedure, or undocumented mise behavior.
  - Obtain the architecture decision described in `HUMAN-REQUEST.md` before changing normative distribution specifications.

- [ ] Rewrite the distribution specifications around the selected mise model.
  - Remove `boundary.lock.json` from Boundary-defined canonical downstream state.
  - Remove the `boundary.lock/v*` format and all requirements to create, read, validate, migrate, or update it.
  - Remove the invariant that an operator-supplied Boundary checkout must be clean and have `HEAD` exactly equal to a committed Boundary lock.
  - Remove the requirement that downstream lifecycle commands themselves compare a supplied checkout revision with a Boundary-owned pin.
  - Define `mise.toml`/the applicable mise configuration and `mise.lock` ownership explicitly. They are normal project/tooling state managed through mise rather than a second Boundary contract format.
  - Define how Boundary source identity enters mise configuration, how `mise lock` records the selected identity, and how locked installation reproduces it under the architecture decision.
  - Define the role of an operator-local source repository separately from portable project state.
  - Rework adoption, installation, health checking, upgrade, and removal semantics so revision selection and locking belong to mise.
  - Specify whether Boundary still needs any generated project-local launcher. Prefer the installed `boundary` executable directly unless a launcher has a remaining semantic responsibility unrelated to locating Python/runtime packages.
  - Preserve the distinction between generated integration state and persistent project contracts.
  - Keep historical documentation historical; do not preserve obsolete lock behavior merely for migration compatibility.
  - Update `docs/spec.md`, focused distribution/state/architecture/lifecycle specs, setup documentation, and applicable native contracts together so the model is orthogonal and consistent.

- [ ] Make Boundary a conventional mise-installable CLI and delete the old lock/check-out mechanics.
  - Ensure the Boundary source repository has the packaging metadata and console entry point required by the selected mise installation model to expose `boundary`.
  - Remove production code whose purpose is reading, writing, validating, comparing, or upgrading `boundary.lock.json`.
  - Remove source-checkout cleanliness/revision matching code that exists only to enforce the old distribution invariant.
  - Remove obsolete install provenance or generated launcher/runtime machinery when mise now owns that responsibility; retain integration materialization only where it still has an independent purpose.
  - Simplify lifecycle commands rather than wrapping obsolete mechanics in new names.
  - Make normal downstream procedure use semantic commands such as `boundary status`, `boundary inspect`, and `boundary contracts check`, with no `PYTHONPATH`, `python -m boundary`, or direct `uv` knowledge.
  - Keep Boundary's own repository-development workflow behind mise tasks as well, so development and consumer instructions do not repeat Python environment plumbing.
  - After the specification pass identifies the implementation paths, update `files.include` to expose only those implementation files and their focused tests for the next iteration.

- [ ] Replace compatibility tests and fixtures with mise-distribution coverage.
  - Delete tests whose only asserted behavior is the existence or semantics of `boundary.lock.json`.
  - Add focused tests for configuration generation/update, exact source identity selection, locked reinstall, upgrade to another identity, health/error reporting, and removal.
  - Exercise the local-Git-repository use case according to the selected distribution architecture.
  - Verify that normal downstream commands execute the mise-installed Boundary CLI rather than a copied Boundary runtime.
  - Verify that generated Spec Kit/runtime state remains non-canonical where still applicable.
  - Keep tests focused on Boundary-visible behavior; do not duplicate mise's own lockfile implementation.

- [ ] Finish the distribution transition and release verification.
  - Remove remaining current-architecture references to `boundary.lock.json`, matching source checkouts, and source-checkout-driven runtime installation outside historical material.
  - Update README/setup/operator guidance after implementation behavior is settled.
  - Run native contract validation and the complete test suite.
  - Run the file-size check and keep changed code/documentation files below 250 lines.
  - Run a clean end-to-end downstream smoke test for the selected mise model and confirm no Boundary-specific revision or dependency lock is created.
  - Remove this TODO when all checks are green.
