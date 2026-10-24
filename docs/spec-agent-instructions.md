# Agent Instructions

Boundary's canonical skills under `skills/` provide concise procedure for scope planning, implementation, and contract evolution. `boundary skills install --directory PATH` optionally materializes them in a caller-selected repository-relative directory. Boundary does not choose or configure an agent runtime.

Before implementation, an agent or coordinating tool must have an explicit request with selected task IDs and exact writes. It runs `boundary pre-change --request FILE`, inspects `boundary inspect --authorized`, changes only allowed targets, runs project checks, and calls `boundary post-change`. Failed post-change results leave the operation open; `boundary post-abandon` records explicit unverified closure when needed.

`boundary status` is a read-only handoff and recovery query. It reports the current worktree operation, scope, status, and whether the current `HEAD` matches the baseline. Agent reasoning may decide whether work is useful or complete; Boundary deterministically checks the recorded scope and Git state.

Contract evolution uses `boundary contracts pre-change`, `boundary contracts check`, and `boundary post-change`. Implementation following contract evolution requires a fresh operation. Agent skills are installed independently of any planning system.
