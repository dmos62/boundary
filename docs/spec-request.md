# Generic Change Request

Boundary does not read task files. A caller that owns a planning system translates its structured task metadata into a versioned request and invokes `boundary pre-change --request FILE` (`-` reads standard input).

The version 1 request is:

```json
{
  "schema": "boundary.pre-change-request/v1",
  "changeId": "feature-42",
  "tasks": [
    {"id": "task-1", "writes": ["src/app.py", "tests/test_app.py"]}
  ],
  "selectedTaskIds": ["task-1"]
}
```

The task array defines canonical order. Task IDs are opaque, unique, nonempty strings. Each `writes` entry is an exact canonical repository-relative file path. The selection is explicit, unique, nonempty, and must identify tasks with at least one write. Boundary rejects duplicate write ownership across tasks. Omission never selects all tasks. Direct request fields are strict so a misspelled key cannot silently reduce or broaden authority.

The caller is responsible for projecting its own planning data faithfully. Boundary validates the normalized request, resolves selected paths against fresh native contracts, and persists the selected evidence. It does not authenticate a source task file or infer paths from prose. The selected task and change IDs provide generic provenance without importing a planning-system schema.

Renames require both source and destination paths. Generated code, formatting, tests, and documentation changes need explicit paths like any other write. No planning or bookkeeping path is implicitly exempt from the post-change check.

A caller may inspect planned targets before pre-change using `boundary inspect PATH...`. That query grants no permission. The request is read afresh at each pre-change; post-change uses the stored operation record rather than mutable planning state.
