# Post-change and Abandonment

`boundary post-change` compares the current Git index and worktree with the operation's stored baseline. It requires unchanged `HEAD`, checks every actual repository write against the exact allowed targets, and fresh-resolves target contract context. An implementation operation cannot modify native contracts; a contract-evolution operation cannot modify ordinary project files. There are no generic planning-file or generated-file exemptions.

A failed check leaves the operation open with its evidence intact. Correct changes within scope and retry, or use `boundary post-abandon`. A successful post-change records exact final target states and closes the operation as `verified`. This proves write-scope compliance, not functional correctness or task acceptance. Post-change never commits, resets, restores, rebases, or otherwise edits project files.

`boundary post-abandon` closes an open operation as `abandoned` without checking its writes or changing project files. It never produces verified output. A fresh operation may target disjoint paths. Dirty paths touched by abandoned work cannot be adopted into a later operation until restored or committed.

Both closing commands require an open operation. Closed operations remain visible through `boundary status` until replaced. Read-only queries report only the current worktree; their results are point-in-time observations.
