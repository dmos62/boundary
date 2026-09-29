# Boundary follow-up plan

Task-selected implementation units are now active in the native authorization model and the Spec Kit adapter. New implementation operations require explicit task selection, persist `selectedTaskIds`, authorize only selected-task writes, and preserve deterministic predecessor carry-forward.

The remaining work should reduce mechanical integration cost and surface lifecycle state earlier without weakening the task-selected authorization model.

## 1. Add stable semantic Boundary entrypoints

Remove packaging/runtime discovery from normal agent procedure.

Required work:

- provide one project-local semantic command surface for `inspect`, `authorize`, `verify`, `status`, and `contracts check`;
- make the command self-locate the installed Boundary runtime without caller-managed `PYTHONPATH`, `uv` cache variables, or knowledge of adapter script paths;
- keep change-system-specific translation behind the adapter while exposing lifecycle names that match Boundary semantics;
- preserve explicit implementation-unit selection; the current Spec Kit gate accepts repeated `--task` values and the workflow overlay transports selection through the temporary `BOUNDARY_TASK_IDS` JSON value;
- support the installed environments Boundary already supports rather than requiring PowerShell when Spec Kit is configured for Bash;
- update generated skills and health checks to use and validate the semantic entrypoint;
- classify the launcher as Boundary-generated integration state and keep it out of downstream canonical semantics;
- add install/reinstall/check coverage once the command shape is settled.

Do not add a global executable requirement or encode operator-local Boundary checkout paths in downstream state.

## 2. Make authorization state cheap to hand off

Expose a compact deterministic status/capsule suitable for coordinators and disposable workers.

It should report at least:

- operation ID and status;
- active change ID;
- selected task IDs, using the task selection already persisted in operation evidence;
- authorized targets;
- resolved primary owners and relevant effective-contract identifiers;
- Git baseline/freshness evidence needed to know whether the operation is still usable.

The representation should be query output derived from operation evidence and current repository state, not another persistent source-of-truth file.

Update agent procedure so a delegated worker can establish its authority from this output instead of rediscovering Boundary packaging.

## 3. Surface workflow-record scope before implementation

Keep durable project records as real writes rather than weakening verification or broadly classifying them as generated state.

Required work:

- update Spec Kit planning/task guidance to call out durable checkpoint, continuation, feedback, and similar project records when the project workflow requires them;
- ensure such paths are represented by explicit `Writes:` metadata when implementation is expected to update them;
- add an early scope/ownership diagnostic over declared writes so unowned ordinary targets are found before implementation authorization;
- keep native contract ownership as the durable authorization story for project records;
- do not auto-create project-specific record contracts and do not hide these writes through adapter-owned classification.

Use the `specs/CONTINUATION.md` / `BOUNDARY-FEEDBACK.md` failure as regression guidance.

## 4. Return machine-readable lifecycle outcomes

Make blocking Boundary results distinguishable to orchestration layers without parsing prose.

Define stable outcome categories for at least:

- scope expansion required;
- contract evolution required;
- invalid or ambiguous adapter state;
- missing external prerequisite;
- stale authorization/current-state mismatch;
- verification failure from undeclared or unowned writes.

Human-readable diagnostics should remain, but structured output must carry the category and the operation/change identifiers available at the failure point.

Do not make Boundary decide whether an outer controller should pause; expose enough semantics for the controller to decide.
