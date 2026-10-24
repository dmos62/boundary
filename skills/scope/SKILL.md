# boundary-scope

Use this skill to plan exact repository-relative targets before opening an implementation operation.

1. Read the caller's task or specification and list every file that implementation may create, modify, delete, or rename. Include both paths of a rename and all generated, formatted, test, and documentation writes.
2. Inspect target context with `boundary inspect PATH...`. Ownership and all applicable contracts are additive. Inspection is read-only and grants no permission.
3. Put exact paths in the caller's structured write declaration. Path-looking prose is not scope. Resolve missing ownership or conflicting contracts before implementation.
4. Select task IDs explicitly and produce the versioned request described in `docs/spec-request.md`. Boundary reads this normalized request, not the planning system's files.
5. Run `boundary pre-change --request FILE` before edits. A missing or failed pre-change leaves implementation unauthorized.

Task progress and semantic acceptance belong to the caller. Boundary checks the requested scope and later actual Git writes.
