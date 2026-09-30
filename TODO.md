# Boundary follow-up plan

Task-selected implementation units are active in the native authorization model and the Spec Kit adapter. New implementation operations require explicit task selection, persist `selectedTaskIds`, authorize only selected-task writes, and preserve deterministic predecessor carry-forward.

Downstream installation now also materializes `.boundary/bin/boundary` as generated project-local integration state. It exposes semantic `inspect`, `authorize`, `verify`, `status`, and `contracts check` entrypoints, self-locates installed runtime and adapter state, and owns a local UV cache so callers no longer reconstruct packaging paths or cache configuration.

The remaining work should make authorization handoff richer, surface lifecycle scope earlier, and provide stable orchestration outcomes without weakening task-selected authorization.

## 1. Make authorization state cheap to hand off

Expand the current minimal `boundary status` result into a compact deterministic status/capsule suitable for coordinators and disposable workers.

It should report at least:

- operation ID and status;
- active change ID;
- selected task IDs, using the task selection already persisted in operation evidence;
- authorized targets;
- resolved primary owners and relevant effective-contract identifiers;
- Git baseline/freshness evidence needed to know whether the operation is still usable.

The representation should be query output derived from operation evidence and current repository state, not another persistent source-of-truth file.

Update agent procedure so a delegated worker can establish its authority from this output instead of rediscovering or rereading raw operation evidence.

## 2. Surface workflow-record scope before implementation

Keep durable project records as real writes rather than weakening verification or broadly classifying them as generated state.

Required work:

- update Spec Kit planning/task guidance to call out durable checkpoint, continuation, feedback, and similar project records when the project workflow requires them;
- ensure such paths are represented by explicit `Writes:` metadata when implementation is expected to update them;
- add an early scope/ownership diagnostic over declared writes so unowned ordinary targets are found before implementation authorization;
- keep native contract ownership as the durable authorization story for project records;
- do not auto-create project-specific record contracts and do not hide these writes through adapter-owned classification.

Use the `specs/CONTINUATION.md` / `BOUNDARY-FEEDBACK.md` failure as regression guidance.

## 3. Return machine-readable lifecycle outcomes

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
