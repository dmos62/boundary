# Boundary Specification

Boundary provides durable native project contracts, effective context for repository targets, and exact worktree change scope for coding agents. It is independent of the system that tracks tasks or specifications.

## Canonical model

Native contracts under `contracts/**/*.contract.md` declare explicit ownership and additive applicability. Every implementation target needs one unambiguous primary owner. Applicable broader contracts continue to constrain nested targets. Contract evolution is separate from implementation.

An external caller supplies an ordered, structured change request with explicit task IDs and exact file writes. Boundary does not read planning files or infer scope from prose. The caller selects one or more task IDs; omission never means every task. Boundary records the selected write union, resolved context, and Git baseline before edits.

The canonical lifecycle is `pre-change → edit → post-change`, with `post-abandon` for unresolved operations. Post-change checks actual Git writes and unchanged `HEAD` against immutable operation evidence. Successful checking proves write-scope compliance only; tests and semantic acceptance remain the caller's responsibility.

Operation evidence lives under `.boundary-state/` in the current worktree. One writer per worktree is assumed, while read-only queries may overlap. Distinct worktrees have independent records. Boundary has no distributed lock or external-service authority.

## Product boundaries

Boundary owns contracts, target context, request validation, pre-change permission, operation records, Git baselines, post-change checks, and agent procedure. A planning system owns its task metadata, selection workflow, progress, and acceptance. It translates those records into the [generic request](spec-request.md) without adding a provider-specific module to Boundary.

Boundary distributes as an installed Python CLI selected by mise. `boundary setup` manages the root `.gitignore` block for local evidence. Optional skill delivery uses an explicit caller-selected directory and has no runtime-specific default.

## Focused specifications

- [Contract semantics](spec-contracts.md)
- [Architecture](spec-architecture.md)
- [Generic request](spec-request.md)
- [Pre-change](spec-pre-change.md)
- [Post-change and abandonment](spec-post-change.md)
- [Lifecycle](spec-lifecycle.md)
- [Agent instructions](spec-agent-instructions.md)
- [Distribution](spec-distribution.md) and [generated state](spec-distribution-state.md)

Historical provider material under `history/` describes earlier behavior and has no current authority.
