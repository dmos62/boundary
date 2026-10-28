# Operation Lifecycle

Boundary's blocking lifecycle is:

```text
boundary pre-change --request request.json
boundary inspect --authorized
# edit only allowed targets; run project checks
boundary post-change
```

If post-change cannot succeed, run `boundary post-abandon` and resolve any dirty targets before reuse. A changed Git `HEAD` blocks post-change; abandonment preserves the files and reports no verification. A fresh pre-change never replaces an open operation.

Contract evolution uses a separate operation kind:

```text
boundary contracts pre-change --change CHANGE_ID contracts/example.contract.md
# edit only listed contract paths
boundary contracts check
boundary post-change
# then request fresh implementation pre-change
```

A contract changed in one operation cannot authorize implementation in that same operation. If implementation discovers an additional write, close or abandon the current operation, update the caller's structured request, and open a fresh operation. An already dirty target needs verified predecessor evidence for the same task identity or a restore or commit.

After `post-change`, commit the verified target bytes before further edits.
If a target was edited after verification but before that checkpoint,
restore its exact verified output before requesting a successor operation.
Committing unverified edits is not a recovery shortcut.

Boundary assumes one writer per worktree; parallel writers use distinct worktrees. It stores no cross-worktree lock and does not manage shared external services. Status and inspection are read-only and can overlap the writer.
