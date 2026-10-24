# Worktree and Generated State

Native contracts and the caller's planning artifacts are ordinary project source. Mise configuration and lock state select the Boundary tool. Boundary operation evidence is local workflow state and is not portable project semantics.

Boundary stores the current or most recently closed operation under the current worktree root in `.boundary-state/current.json`. It retains predecessor records only while current verified carry-forward evidence needs them. Evidence may disappear when the worktree is deleted. Boundary does not write records, probes, archives, or exclusions under `.git/**`.

`boundary integration install` materializes Boundary's agent skills and manages one delimited block in the root `.gitignore`. The block ignores `.boundary-state/` and Boundary-generated skill paths. The `.gitignore` edit is visible project state. Install, check, and remove validate the block and preserve unrelated rules. Install and remove refuse an open operation.

Generated skills are recreatable from the installed Boundary package. Boundary does not classify or hide an external planning system's files. Other changed paths remain visible to Git and subject to the current operation's exact scope.
