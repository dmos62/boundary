# TODO

## Finish Linux Spec Kit script-mode rollout

The root cause is resolved in Boundary-controlled lifecycle code: older bootstrap and host-install paths passed `--script ps` unconditionally. Pinned Spec Kit 1.0.10 selects `sh` on non-Windows hosts when no explicit mode is supplied, records the selection in `.specify/init-options.json`, and reuses that saved selection in later integration operations.

The implementation now delegates clean initialization to Spec Kit, preserves an existing project selection, and exposes `BOUNDARY_SPECKIT_SCRIPT=sh|ps|py` only for an explicit mode transition. When Codex is already active, the transition uses `specify integration upgrade` so Spec Kit regenerates its own scripts and generated integration files. Boundary does not patch generated scripts or materialized `speckit-*` skills.

Development bootstrap deliberately re-runs supported Spec Kit initialization so a Boundary source checkout created by the old forced-PowerShell bootstrap can be repaired by the host-aware Spec Kit default. An explicit PowerShell selection still requires `pwsh`.

Pinned Spec Kit 1.0.10 owns `.specify/.gitignore`; its stock ignore file currently excludes machine-local feature selection and extension local configuration, while other `.specify/` project files remain visible. Do not broaden Boundary worktree exclusions to hide shared Spec Kit state while the persistent/generated ownership decision below remains open.

### Verify downstream recovery end to end

- On Linux with the real pinned Spec Kit 1.0.10, install into a clean temporary downstream repository and verify `.specify/init-options.json` selects `sh`.
- Verify the generated core scripts and materialized `speckit-*` skills reference the same shell implementation, `consumer.py check` passes, and the first Spec Kit workflow step executes.
- Reproduce an affected project with saved `ps` mode and no `pwsh`: normal install/check must preserve the selection and fail with the prerequisite message.
- Run reinstall or upgrade with `BOUNDARY_SPECKIT_SCRIPT=sh` and verify Spec Kit regenerates a coherent shell-mode project without direct generated-file edits.
- Verify an explicit PowerShell selection remains preserved and still requires `pwsh`.
- Determine whether Spec Kit leaves an unused script implementation from the previous mode after `integration upgrade`; record whether that is expected host state or requires an upstream-supported cleanup step.
- Inspect Git status after recovery and record which Spec Kit configuration changes remain visible and therefore require project review or commit.

### Define Spec Kit project-state ownership

- Classify the pinned Spec Kit `.specify/` paths as persistent project configuration, shareable generated state, or machine-local disposable state.
- Decide whether the stock `.specify/.gitignore` already expresses the intended ownership model or needs a supported Spec Kit-managed adjustment.
- Keep `.specify/` itself visible; do not add a broad Boundary ignore for the directory.
- Keep persistent or shared Spec Kit configuration reviewable in Git.
- If persistent ownership semantics change, perform that specification/contract evolution as a separate operation, validate it, and obtain fresh implementation authorization before changing runtime behavior.
- Keep `docs/spec-distribution.md`, downstream consumer exclusion logic, and the repository-tooling contract aligned after that transition.

### Finish regression coverage

- Add a real pinned-CLI Linux integration test for clean installation and shell-mode generation.
- Add recovery coverage for a previously forced `ps` project using the supported reinstall/upgrade lifecycle.
- Verify generated script mode and generated skill commands stay coherent.
- Cover `.specify/.gitignore` so only the intended disposable host files are hidden and persistent Spec Kit artifacts remain visible.
- Retain clean-consumer coverage proving Boundary-owned generated paths remain outside normal downstream status.
- Keep `files.include` focused on these tests until the rollout is complete.

### Finalize documentation

- Update downstream and development setup text with any behavior discovered by the real-CLI recovery tests.
- Finalize generated-state wording after the `.specify/` ownership decision.
- Remove this TODO when recovery validation, ownership semantics, regression coverage, and documentation are complete.
