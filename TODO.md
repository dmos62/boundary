# Boundary follow-up plan

Task-selected implementation units are active in the native authorization model and the Spec Kit adapter. New implementation operations require explicit task selection, persist `selectedTaskIds`, authorize only selected-task writes, and preserve deterministic predecessor carry-forward.

Downstream installation materializes `.boundary/bin/boundary` as generated project-local integration state. It exposes semantic `inspect`, `authorize`, `verify`, `status`, and `contracts check` entrypoints, self-locates installed runtime and adapter state, and owns a local UV cache so callers no longer reconstruct packaging paths or cache configuration.

Authorization handoff is complete at the procedural layer. The compact `boundary.status/v2` projection reports current operation identity and status, change identity, selected tasks, authorized target evidence, optional recorded target contexts, and current-versus-baseline Git HEAD freshness. Canonical implementation procedure now requires delegated workers to establish authority from that status projection before writing rather than rediscovering raw operation evidence or reconstructing authority from mutable task files.

The remaining work should surface lifecycle scope earlier and provide stable orchestration outcomes without weakening task-selected authorization.

## 1. Surface workflow-record scope before implementation

The architecture now distinguishes declared-scope readiness from implementation authorization.

The declared-scope preflight is non-authorizing planning/task-readiness work over the deterministic ordered union of structured task writes. It uses Boundary effective target inspection, creates no operation record or Git baseline, does not select an implementation unit, and cannot grant authority to unselected tasks. Fresh selected-unit authorization remains authoritative.

Durable checkpoint, continuation, feedback, and similar project records remain ordinary writes unless the host change system actually owns them. When implementation is expected to update such records, task generation must declare their exact paths so ownership defects can be surfaced before implementation.

Remaining work:

- update the canonical Boundary scope skill and concrete Spec Kit task-generation guidance to call out required durable project records and require exact `Writes:` declarations for them;
- wire the Spec Kit task-readiness path to inspect the complete declared write projection through Boundary rather than reproducing contract resolution;
- make unowned and ambiguous declared targets visible before implementation entry without persisting another lifecycle artifact or changing selected-unit authorization semantics;
- add focused tests covering the `specs/CONTINUATION.md` / `BOUNDARY-FEEDBACK.md` regression shape and proving that preflight information grants no implementation authority.

Do not auto-create project-specific record contracts and do not hide these writes through adapter-owned classification.

Use the `specs/CONTINUATION.md` / `BOUNDARY-FEEDBACK.md` failure as regression guidance.

## 2. Return machine-readable lifecycle outcomes

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
