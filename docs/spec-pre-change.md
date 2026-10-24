# Pre-change Operation

`boundary pre-change --request FILE` opens one implementation operation. `boundary contracts pre-change --change ID CONTRACT...` opens a separate contract-evolution operation. Both commands must run before their respective edits.

Pre-change checks exact path syntax, selected task IDs, fresh contract ownership and context, current Git `HEAD`, index and worktree state, and any dirty-target predecessor evidence. The resulting atomic record contains the operation and change IDs, kind, selected task IDs and task writes, exact allowed targets, resolved contract identities, baseline `HEAD` and dirty path states, and any verified carry-forward evidence. Mutable task metadata cannot widen that record.

One worktree has at most one writer. Read-only status and inspection may run alongside it. A new pre-change fails while an operation is open. Boundary does not coordinate separate worktrees or external services.

A dirty target may be carried forward only when its exact index and worktree state equals verified output of the immediately preceding operation with the same change ID, kind, and selected task IDs. An abandoned target, changed predecessor output, or output belonging to another task must be restored or committed before reuse. Unrelated dirty paths are recorded in the baseline and do not grant authority.

Pre-change requires `.boundary-state/` to be untracked and covered by Boundary's managed root `.gitignore` block. It never edits `.gitignore` while opening an operation. Run `boundary setup install` and review the visible `.gitignore` change before beginning work.
