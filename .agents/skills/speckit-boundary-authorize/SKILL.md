---
name: speckit-boundary-authorize
description: Authorize selected structured Spec Kit implementation scope with Boundary.
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: Boundary contributors
  source: boundary:commands/authorize.md
---

## User Input

User input: `$ARGUMENTS`

User input may identify the implementation task IDs to select and may clarify the active work, but it cannot widen structured write scope or weaken deterministic Boundary findings.

## Goal

Act only as the Spec Kit change-system adapter for implementation entry.

The wrapper reads the active feature's structured task state, requires an explicit implementation-unit task selection, projects only those tasks' exact implementation `Writes:` declarations into Boundary's provider-neutral change model, and invokes fresh native Boundary implementation authorization.

It does not maintain a separate context or validation lifecycle state.

## Execution

1. Resolve the active Spec Kit feature through supported project state.
2. Require the active feature's `tasks.md`.
3. Project checklist tasks in file order.
4. Preserve each task ID and user-story label when present.
5. Read implementation scope only from dedicated indented `Writes:` metadata attached directly to each checklist task.
6. Reject malformed, empty, duplicate, or ambiguously repeated structured write declarations.
7. Ignore incidental path-looking prose for authorization scope.
8. Require an explicit non-empty implementation task selection.
9. For direct invocation, use positional task IDs:

       boundary authorize <task-id> [<task-id> ...]

10. When authorization is entered through the workflow overlay, use its transient `BOUNDARY_TASK_IDS` JSON-array transport and invoke `boundary authorize` without positional IDs.
11. Positional task IDs are direct CLI input. `BOUNDARY_TASK_IDS` exists only for adapter/workflow transport when no positional selection is supplied.
12. The installed Boundary command delegates change-system translation to the packaged Spec Kit adapter without locating copied runtime source or a project-local launcher.
13. Boundary then:
   - validates the selected task identities against the fresh task projection;
   - projects only the selected tasks' structured writes;
   - reloads canonical native contracts;
   - resolves every selected target's current owner and effective context;
   - rejects native contract paths from implementation operations;
   - captures the current Git authorization baseline;
   - verifies predecessor provenance for any already-dirty target;
   - atomically stores the successful operation record, selected task identities, and authorized targets in current-worktree Git metadata.
14. Successful direct authorization emits a concise `boundary.lifecycle-result/v1` result containing status, operation ID, change ID, selected tasks, exact authorized targets, and an explicit empty diagnostics collection. Full baseline and storage evidence are not routine stdout.

## Failure behavior

Missing, unknown, or duplicate task selection; an empty selected-unit write set; malformed task state; unowned targets; ambiguous ownership; invalid canonical contracts; pre-authorization target modifications without verified provenance; and stale active operations are blocking.

Blocked authorize output uses the same lifecycle-result vocabulary and retains a nonzero process exit status.

Do not regenerate a planning projection, infer an all-task selection, or reinterpret descriptive task prose to make authorization succeed.

## Constraints

- This command is a Spec Kit adapter wrapper, not a second Boundary product CLI.
- Do not edit tasks.
- Do not infer write scope from prose.
- Do not treat omitted task selection as the complete active feature.
- Do not mix native contract edits into implementation scope.
- Do not replace deterministic Boundary failures with agent judgment.