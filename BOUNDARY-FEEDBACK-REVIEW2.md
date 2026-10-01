# Boundary feedback follow-up review

## Purpose and authority

This review is the source-backed follow-up to `BOUNDARY-FEEDBACK-REVIEW1.md`.

Review1 and `../gui-auto2/BOUNDARY-FEEDBACK.md` are historical inputs. They are useful for reconstructing the 2026-09-25 through 2026-09-29 incidents, but they do not define current Boundary behavior. Current authority comes from `docs/spec*.md`, applicable native contracts under `contracts/`, current source, and current automated/integration tests.

The follow-up separates specified semantics, concrete implementation, automated evidence, runtime/distribution evidence, and remaining limitations. Documentation statements are not counted as implementation evidence by themselves.

## 1. Executive status

| Review1 concern or question | Status | Current answer and evidence |
|---|---|---|
| Feature-wide flattened authorization obscured the active implementation unit. | addressed | `docs/spec.md`, `docs/spec-authorization.md`, and `docs/spec-change-adapter.md` define an implementation unit as an explicit non-empty task selection. `ChangeWriteSet.select_tasks()` and `authorize_implementation()` authorize only selected task writes. `tests/test_task_selected_units.py` covers sequential and multi-task units. |
| Task provenance existed but did not constrain authority. | addressed | Selected task identities are now authority input and persisted evidence. `OperationRecord` stores `selectedTaskIds`, selected task evidence, and exact targets; `record_validation.py` requires targets to equal the selected-task write union. `tests/test_operation_record_task_selection.py` exercises malformed persisted evidence. |
| A feature should be able to contain several implementation units. | addressed | The lifecycle permits multiple verified authorization epochs for one change. `authorization/service.py` requires predecessor closure and supports exact carry-forward; `tests/test_task_selected_units.py` and `tests/test_authorization_lifecycle.py` cover sequential units. |
| Implementation units should map cleanly to architectural owners. | superseded / intentionally out of scope | Current specs explicitly separate unit membership from ownership. A selected unit may span multiple owners, and ownership is resolved per target. Ownership never widens selection. |
| Coordinated multi-owner work needs a synthetic task/owner authority identity. | superseded / intentionally out of scope | A selected unit may directly span several owners. `tests/test_task_selected_units.py` verifies that each selected target records its own owner without introducing synthetic authority. |
| Every task or architectural owner should require its own Boundary operation. | superseded / intentionally out of scope | Boundary permits explicit multi-task and multi-owner selections when they form one coherent implementation unit. It requires explicit selection, not one-operation-per-task or one-operation-per-owner structure. |
| T012 should not receive `clipboard.rs` authority merely because another feature task declared it. | addressed | Selected-task authorization removes the old behavior. A T012-only authorization contains only T012 writes; a write to a path declared only by T009 is an `UNDECLARED_WRITE`. Same-owner status does not change this. |
| Same-owner scope expansion should have implicit permission or lighter authority semantics. | superseded / intentionally out of scope | The specs allow different coordination diagnostics but deliberately require the same authority transition: close the current epoch, update/select structured scope, and fresh-authorize. `tests/test_native_verification.py` covers same-owner undeclared-write rejection. |
| Cross-owner scope expansion requires a distinct permission model. | superseded / intentionally out of scope | Cross-owner discovery may justify different coordination diagnostics, but it does not change write authority. Fresh explicit selection and authorization are required in both cases. |
| Common Boundary operations required rediscovery of Python paths, uv plumbing, copied runtimes, or adapter scripts. | addressed | `pyproject.toml` exposes the installed `boundary` console script. `src/boundary/cli/main.py` provides inspect, authorize, verify, status, contracts check, and integration lifecycle commands. Distribution tests verify the installed CLI outside the consumer repository. |
| Semantic lifecycle phases were not obvious or uniform. | addressed | `docs/spec-lifecycle.md` defines `authorize → implement → verify`; contract evolution is separate. Canonical skills and integration wrappers use the installed semantic CLI instead of private runtime paths. |
| Authorization state was expensive to hand to workers. | addressed | `authorization/handoff.py` projects `boundary.authorization-handoff/v1` from the current historical operation plus fresh Git HEAD. `boundary status` exposes it directly, and `status_feature()` adds active-feature match state. Focused status tests cover absent, matching, and mismatched operations. |
| Cross-task work within one architectural component is necessarily an architectural violation. | superseded / intentionally out of scope | Cross-task work is permitted when the next explicit unit selects the relevant task set. Architectural ownership supplies context and constraints but is not task membership. |
| Workflow/process records needed predictable treatment. | superseded / intentionally out of scope | Boundary intentionally has no universal workflow-record authority category. Durable checkpoints and feedback files are ordinary writes unless the change system genuinely owns them. `boundary-scope` requires exact declaration, and declared-scope preflight resolves their ownership when declared. |
| Late discovery of unowned durable records should be reduced. | partially addressed | Planning guidance and `preflight_declared_scope()` catch invalid, ambiguous, or unowned declared writes before authorization. They cannot discover a required path that task generation omitted entirely. This limitation is explicit in the current lifecycle model. |
| Boundary outcomes should help orchestration distinguish lifecycle failures. | addressed | `boundary.lifecycle-outcome/v1` classifies invalid adapter state, missing prerequisites, stale authorization, verification write-scope failures, and required Boundary transitions. `tests/test_lifecycle_outcomes.py` covers representative mappings. |
| Boundary should decide whether a controller pauses, retries, asks a human, or continues. | superseded / intentionally out of scope | `docs/spec-lifecycle.md` assigns those policy decisions to the outer controller. Boundary reports deterministic state and required Boundary transitions but does not classify ordinary test failures or choose controller policy. |
| Undeclared administrative writes should be permitted to reduce friction. | superseded / intentionally out of scope | Current verification intentionally rejects ordinary undeclared writes, including same-owner writes and durable project records. `tests/test_native_verification.py` preserves this enforcement. |
| Contract edits and dependent implementation could be combined for convenience. | superseded / intentionally out of scope | Operation-kind separation remains deliberate. Implementation rejects native contract writes; contract evolution rejects ordinary project writes; dependent implementation requires fresh authorization afterward. |
| Runtime setup should respect the configured Spec Kit script mode instead of requiring PowerShell in Bash mode. | addressed | `boundary_host.discovery` dispatches Bash, PowerShell, or Python prerequisite scripts from `.specify/init-options.json`; `host_runtime.require_script_runtime()` requires only the selected runtime. `tests/test_spec_kit_script_modes.py` covers routing and transitions. |
| The Spec Kit `BRANCH` metadata ambiguity should be fixed by Boundary. | superseded / intentionally out of scope | Boundary does not consume that field. Active-feature discovery uses `SPECIFY_FEATURE_DIRECTORY` or host `FEATURE_DIR`; the adapter treats the resolved feature-directory name as opaque change identity. |

## 2. Current implementation-unit model

The current model answers Review1's central architecture question without introducing owner-derived units.

An implementation unit is an explicit selection of one or more task identities from the active change. The adapter preserves canonical host task order, rejects missing, duplicate, or unknown selections, and rejects a selected unit whose structured writes are empty. The authorized write set is the deterministic ordered union of only those selected tasks' `Writes:` metadata.

Concrete implementation is in `src/boundary/authorization/model.py` and `engine.py`. `ChangeWriteSet.writes` still exposes the complete change-level union, but only for planning and declared-scope preflight. Authorization calls `change.select_tasks(...)` and never falls back to that feature-wide union.

Ownership is a separate calculation. Every selected target is fresh-resolved through the native contract graph and records one primary owner plus an effective-context identity. A selected unit may span several owners. Conversely, a target sharing an owner with an authorized path gains no authority unless a selected task declares it.

Historical evidence is stronger than it was in Review1. `OperationRecord` persists the selected task identities, selected task write evidence, exact authorized targets, owner evidence, and effective-context identities. `record_validation.py` rejects persisted implementation records whose target order or membership differs from the selected-task write union or whose target evidence omits owner/context identity. `tests/test_operation_record_task_selection.py` covers those fail-closed cases.

## 3. T012 / `clipboard.rs` under current semantics

The historical scenario can now be stated directly.

Assume T012 declares only calibration test and manifest writes, while T009 declares `crates/desktop-host-windows/src/clipboard.rs`. Selecting only T012 authorizes only T012's declared writes. The fact that T009 is part of the same feature does not add `clipboard.rs`, and the fact that both tasks may resolve to `desktop-host-windows` does not add it either.

If implementation writes `clipboard.rs` during the T012 operation, verification derives that Git write from the historical baseline and reports `UNDECLARED_WRITE`. `src/boundary/verification/checks.py` performs this exact authorized-set comparison. `tests/test_native_verification.py::test_rejects_undeclared_write_in_same_owner` protects the same authority rule independently of owner boundaries.

The supported transition is to stop before the extra write when discovered, verify and close the current operation, then fresh-authorize the next explicit task selection. If `clipboard.rs` is already declared by T009, the successor may select T009, optionally together with other tasks. If the path is undeclared by every task, structured task scope must be refined first. `tests/test_task_selected_units.py` demonstrates fresh selection, canonical host ordering, and verified predecessor carry-forward.

## 4. Lifecycle and worker handoff

The mandatory implementation lifecycle is now explicit and mechanically represented: `authorize → implement → verify`.

Authorization creates one atomic historical operation record. Verification consumes that record rather than re-reading mutable task scope. An unverified active operation cannot be silently replaced, and a changed Git HEAD blocks closure. Verified dirty target output can carry into a successor only when its exact Git state matches the predecessor's recorded final state.

`boundary status` adds the worker-handoff surface Review1 requested without becoming another authority source. The `boundary.authorization-handoff/v1` document contains operation/change identity, kind, lifecycle status, selected task IDs, exact target evidence, contract-graph identity, authorization-time HEAD, current HEAD, and `headMatchesBaseline`. `tests/test_spec_kit_status_projection.py` verifies active-feature relationship reporting; the product CLI implementation lives in `src/boundary/cli/status.py`.

The handoff intentionally does not re-resolve contracts, select tasks, widen scope, or close the operation. A matching HEAD is a useful freshness fact, not proof that semantic contract context is unchanged. Authoritative closure remains `boundary verify`.

## 5. CLI and distribution ergonomics

Review1's mechanical-discovery problem is independently addressed by the distribution model.

`pyproject.toml` installs `boundary = "boundary.cli:main"`. The wheel packages provider-neutral Boundary core plus the concrete Spec Kit host runtime and force-includes canonical skills, adapters, commands, workflow overlay, and preset assets. The public surface includes `boundary inspect`, `boundary authorize --task ...`, `boundary verify`, `boundary status`, `boundary contracts check`, and `boundary integration install|check|remove`.

The source-level distribution tests verify the command surface and reject retired launcher/runtime assumptions. The mise integration test installs Boundary into mise-managed tool state, resolves the executable outside the consumer repository, exercises integration install/check/remove, and verifies that `.boundary`, `.specify/boundary-runtime`, and `boundary.lock.json` are unnecessary. The lock test verifies exact Boundary Git source identity remains fixed until an explicit mise lock bump.

The carried-forward distribution-focused run passed 9 tests. The current full-suite baseline supplied to this follow-up is not green because of the separate declared-scope preflight defect described in section 9; that failure does not reintroduce the old distribution path.

## 6. Workflow records and planning/preflight

Current Boundary deliberately treats checkpoints, continuation records, feedback files, and similar durable artifacts as ordinary repository writes unless the active change system genuinely owns them as bookkeeping.

The prevention mechanism is explicit planning, not a special authority category. `skills/scope/SKILL.md` requires durable project/workflow records to appear in exact structured writes when implementation is expected to modify them. The Spec Kit adapter then computes the complete declared write union and `preflight_declared_scope()` resolves every declared target through the fresh native contract graph before implementation entry.

That preflight is non-authorizing. It creates no operation record, captures no Git baseline, selects no unit, and grants no permission. Later authorization independently reloads the selected tasks and current contracts.

This answers the historical `specs/CONTINUATION.md` problem when the record is correctly planned and owned. It does not automatically discover an omitted record. The analogous `.gitignore` incident therefore remains only partially prevented: if task generation never declares the required setup write, preflight has nothing to inspect and the normal scope-expansion/contract-evolution path is still required when implementation discovers it.

During this follow-up, the existing focused unowned-preflight test exposed a concrete implementation bug: the unowned-target branch attempted to chain from an exception variable that did not exist on that path, producing `UnboundLocalError` instead of `SpecKitAdapterError`. The source change accompanying this review removes that invalid exception chaining. Post-change focused and full-suite validation remains required before the fix is considered test-confirmed.

## 7. Machine-readable outcomes and orchestration

Boundary now exposes blocked results through `boundary.lifecycle-outcome/v1`.

`src/boundary/outcomes.py` classifies structured diagnostic codes into stable categories including `scope-expansion-required`, `contract-evolution-required`, `invalid-adapter-state`, `missing-external-prerequisite`, `stale-authorization`, and `verification-write-scope-failure`. It can also name a required Boundary transition. `tests/test_lifecycle_outcomes.py` covers invalid task selection, missing prerequisites, and an unowned verification write requiring contract evolution.

This is enough for a controller to distinguish Boundary lifecycle states without parsing prose. It does not make Boundary the controller. Ordinary implementation/test failures and policy such as pause, retry, ask a human, or continue another activity remain outside Boundary's deterministic authority model.

## 8. Original runtime/setup incident closure

The 2026-09-25 script-runtime incidents are implemented fixes, not documentation-only promises. Fresh Spec Kit projects do not force a script mode unless `BOUNDARY_SPECKIT_SCRIPT` is explicitly set. Existing projects preserve `.specify/init-options.json` unless that override requests a supported transition. When the active integration is already Codex, a mode change goes through Spec Kit's forced integration-upgrade lifecycle.

Active-feature discovery dispatches to Bash, PowerShell, or Python according to the selected mode, and runtime prerequisite checks mirror that selection. Bash mode therefore has no Boundary-side PowerShell dependency. `tests/test_spec_kit_script_modes.py` covers these behaviors, including retained inactive script-variant residue.

The historical `.gitignore` incident has only conditional closure: current planning/preflight catches ownership defects for paths that are actually declared, but it does not heuristically discover omitted setup writes.

The historical Spec Kit `BRANCH` observation is outside Boundary semantics. Boundary uses the resolved feature directory as its opaque change identity and does not consume that host metadata field.

## 9. Remaining gaps and rejected directions

The current evidence demonstrates one concrete implementation defect in declared-scope preflight, and this review includes the minimal source correction. The remaining work is validation: rerun the focused adapter test, broader lifecycle coverage, contract validation, and the full suite because source changed.

One product limitation remains deliberate and observable: declared-scope preflight cannot detect writes omitted entirely from structured task scope. This means late scope discovery is still possible when planning misses a required durable record or setup file. The current design chooses deterministic explicit scope plus verification rather than heuristic authority discovery.

No current evidence supports reopening these rejected directions: implicit feature-wide authorization; owner-derived unit membership; automatic same-owner scope widening; a universal workflow-record permission category; combined contract-evolution/implementation epochs; controller pause policy inside Boundary; or a return to copied runtimes and Boundary-owned revision locks.

Accordingly, the only recommendation from this follow-up is to validate the preflight bug fix and keep the documented omitted-write limitation visible in planning guidance and regression coverage. No README or specification correction is demonstrated by the current evidence.
