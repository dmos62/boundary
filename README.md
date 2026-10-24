# Boundary

Boundary gives coding agents exact file scope under durable project contracts. An external tool supplies selected task IDs and declared writes; Boundary captures a Git baseline before edits and checks actual writes afterward.

## Basic use

Install Boundary from its Git source with mise, then in the target worktree run:

```text
boundary integration install
boundary integration check
```

The install command adds Boundary's agent skills and a visible managed block to the root `.gitignore` for `.boundary-state/` and generated skills. Review and commit that project change according to your normal workflow.

A task system supplies a normalized request:

```json
{
  "schema": "boundary.pre-change-request/v1",
  "changeId": "feature-42",
  "tasks": [{"id": "task-1", "writes": ["src/app.py"]}],
  "selectedTaskIds": ["task-1"]
}
```

Then run:

```text
boundary pre-change --request request.json
boundary inspect --authorized
# edit and run project checks
boundary post-change
```

`post-change` closes only when `HEAD` is unchanged and actual writes fit the stored scope. A failed check leaves the operation open. `boundary post-abandon` closes it explicitly without verifying or altering project files. `boundary status` reports the current worktree's operation.

For native contracts, use `boundary contracts pre-change --change ID CONTRACT...`, edit those contracts, run `boundary contracts check`, then `boundary post-change`. Dependent implementation needs a fresh pre-change.

## Ownership and distribution

Boundary reads no planning-system task format. A caller translates its own structured metadata into the [generic request](docs/spec-request.md). Boundary owns [native contracts](docs/spec-contracts.md), [operation evidence](docs/spec-pre-change.md), and [actual-write checks](docs/spec-post-change.md). It does not track task progress or decide whether a feature is complete.

The CLI is installed through ordinary mise project configuration and `mise.lock`; it has no separate Boundary lock or copied runtime. Codex and Claude skill materializers use the same canonical procedure under `skills/`.

See [downstream setup](docs/setup-downstream.md), [development setup](docs/setup-development.md), and the [specification](docs/spec.md).
