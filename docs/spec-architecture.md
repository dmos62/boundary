# Boundary Architecture

Boundary owns native contracts, effective target context, exact operation scope, worktree-local evidence, and post-change Git checks. External tools own task records, work selection, and semantic acceptance.

The `request` package validates a versioned generic task projection. `pre_change` resolves selected paths against fresh contracts and opens an operation. `operation` owns records, Git path states, status projection, and atomic worktree storage. `post_change` derives actual writes, checks the stored scope, and closes or abandons an operation. `cli` exposes the installed commands. `context`, `contracts`, and `repository` remain independent native engines.

A caller translates its own task metadata into `boundary.pre-change-request/v1` JSON. Boundary has no provider plugin registry, planning-system parser, or host-specific path classifier. The request transport is a thin boundary over the same native services used by the CLI.

Canonical procedure remains under `skills/`. Optional skill delivery accepts a repository-relative destination supplied by the caller; Boundary has no agent-runtime adapters or discovery-path defaults. Mise selects and installs the CLI. `boundary setup install` manages only the local-evidence ignore rule.

Separate worktrees have independent operation records. Boundary assumes one writer per worktree and allows read-only queries alongside it. It does not coordinate shared external systems or integration of branches.
