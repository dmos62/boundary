# TODO

## Finish Linux Spec Kit script-mode rollout

The root cause is resolved in Boundary-controlled lifecycle code: older bootstrap and host-install paths passed `--script ps` unconditionally. Pinned Spec Kit 1.0.10 selects `sh` on non-Windows hosts when no explicit mode is supplied, records the selection in `.specify/init-options.json`, and reuses that saved selection in later integration operations.

The implementation now delegates clean initialization to Spec Kit, preserves an existing project selection, and exposes `BOUNDARY_SPECKIT_SCRIPT=sh|ps|py` only for an explicit mode transition. When Codex is already active, the transition uses `specify integration upgrade` so Spec Kit regenerates its own scripts and generated integration files. Boundary does not patch generated scripts or materialized `speckit-*` skills.

Development bootstrap deliberately re-runs supported Spec Kit initialization so a Boundary source checkout created by the old forced-PowerShell bootstrap can be repaired by the host-aware Spec Kit default. An explicit PowerShell selection still requires `pwsh`.

Pinned Spec Kit 1.0.10 owns `.specify/.gitignore`; its stock file ignores only the machine-local feature pointer and per-machine extension local configuration. Shared `.specify/` project state remains visible. Spec Kit also scopes stale-script cleanup to the selected script variant, so a `ps` to `sh` integration upgrade can leave the old `.specify/scripts/powershell/` directory present. The saved selection and regenerated skills use `sh`; Boundary treats the inactive directory as host-generated Spec Kit state and does not delete it directly.

Real pinned-CLI Linux coverage now lives in `tests/test_install_real_cli.py`. It builds a clean temporary Boundary source checkout and downstream Git repository so consumer source-cleanliness and revision checks remain active during the test.

### Verify downstream recovery end to end

- Run the real pinned-CLI Linux test after this change and confirm clean installation selects `sh`, `consumer.py check` passes, the generated `speckit-plan` skill references Bash, and the shell workflow helper executes.
- Confirm the saved-`ps` recovery case fails normal install/check without `pwsh`, preserves `ps`, succeeds with `BOUNDARY_SPECKIT_SCRIPT=sh`, and leaves the inactive PowerShell script directory untouched.
- Record the exact visible Git status produced by recovery and use it as input to the project-state ownership decision below.

### Define Spec Kit project-state ownership

- Classify the pinned Spec Kit `.specify/` paths and materialized core `speckit-*` skills as persistent project configuration, shareable generated state, or machine-local disposable state.
- Decide whether the stock `.specify/.gitignore` already expresses the intended ownership model or needs a supported Spec Kit-managed adjustment.
- Keep `.specify/` itself visible; do not add a broad Boundary ignore for the directory.
- Keep persistent or shared Spec Kit configuration reviewable in Git.
- Treat inactive script-variant directories retained by Spec Kit mode transitions as host-generated state unless Spec Kit provides a supported cleanup lifecycle.
- If persistent ownership semantics change, perform that specification/contract evolution as a separate operation, validate it, and obtain fresh implementation authorization before changing runtime behavior.
- Keep `docs/spec-distribution.md`, downstream consumer exclusion logic, and the repository-tooling contract aligned after that transition.

### Finish regression coverage

- Retain clean-consumer coverage proving Boundary-owned generated paths remain outside normal downstream status.
- Keep `files.include` focused on the real CLI recovery path until the rollout is complete.

### Finalize documentation

- Finalize generated-state wording after the `.specify/` ownership decision.
- Remove this TODO when recovery validation, ownership semantics, regression coverage, and documentation are complete.
