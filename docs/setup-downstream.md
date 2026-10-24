# Downstream Boundary Setup

Install the `boundary-cli` Git source through mise and commit the project's mise configuration and lock state. Boundary has no second revision lock and does not require a local source checkout.

After installing the locked tool, run `boundary integration install` and `boundary integration check`. Review the visible root `.gitignore` block. It ignores `.boundary-state/` and Boundary-generated agent skills; unrelated project rules remain intact. Integration install and remove require that no Boundary operation be open.

A planning tool projects selected tasks and exact writes into [the generic request](spec-request.md). It invokes `boundary pre-change --request FILE` before edits and `boundary post-change` afterward. `boundary post-abandon` explicitly closes an operation that cannot pass. `boundary status` and `boundary inspect --authorized` are read-only.

## Upgrade from Git-metadata evidence

Before upgrading, use the old Boundary version to verify every open operation or complete its supported recovery procedure. Preserve or checkpoint project changes under the old workflow. The new version does not import `.git/boundary` records and refuses lifecycle commands while legacy evidence remains in the current worktree's Git directory. After resolving the old operation, manually remove that old Boundary record directory and only the old Boundary-managed block from the worktree's Git `info/exclude`. Do not remove unrelated Git metadata or exclusion rules. Run the new `boundary integration install` to establish the root `.gitignore` block, then check it and begin fresh operations.

Separate worktrees have independent evidence and require their own checks. Deleting a worktree may delete its local operation evidence. Boundary never treats `boundary status` as permission for an external installer or deployment; that policy belongs to the caller.
