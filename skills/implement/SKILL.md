# boundary-implement

Use this skill after `boundary pre-change` reports an open implementation operation.

1. Run `boundary inspect --authorized` and read the selected task IDs, exact allowed targets, and effective contract context. Require the recorded Git `HEAD` to match the current worktree.
2. Change only allowed targets. Run relevant tests and checks; their success does not replace Boundary's write check.
3. Run `boundary post-change`. If it blocks, correct work within scope and retry. If the operation cannot pass, run `boundary post-abandon`; it preserves files and records no verification.
4. For an additional write, close or abandon the current operation, update the caller's structured request, and run a fresh pre-change before editing that path.

Native contracts require a separate contract-evolution operation. Dirty output may carry forward only when Boundary validates exact verified predecessor evidence for the same task identity. Another task touching the same dirty file requires a restore or commit first.

`boundary status` is a read-only recovery query. The worktree has one writer; other processes may inspect it without changing authority.
