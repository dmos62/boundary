# boundary-contracts

Use this skill to evolve persistent Boundary contracts deliberately.

1. Inspect the current contract graph and target context. Identify exact `contracts/**/*.contract.md` paths to create, modify, or delete.
2. Run `boundary contracts pre-change --change CHANGE_ID CONTRACT...` before editing. Modify only listed contract paths.
3. Run `boundary contracts check` to validate structure and additive applicability.
4. Run `boundary post-change` to check actual writes and close the operation. A blocked result leaves it open; `boundary post-abandon` closes it without verification.
5. Run a fresh implementation pre-change after verified contract evolution. New contract text never retroactively permits ordinary implementation writes in the same operation.

Keep architectural decisions in concise native contracts. A structural check does not prove that the prose expresses the intended architecture.
