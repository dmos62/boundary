---
schema: boundary.contract/v1
id: boundary-authorization
owns:
  - src/boundary/authorization/**
depends_on:
  - boundary-context
  - boundary-native-contracts
  - boundary-repository
---

# Operation Authorization

## Purpose

Authorize exact operation write scope against fresh contracts and current Git state.

## Invariants

- Implementation scope comes only from explicit structured write declarations.
- Implementation authorization requires an explicit ordered selection of one or more task identities from the active change.
- Authorized implementation targets are the deterministic ordered union of the selected tasks' structured writes; unselected tasks grant no write authority.
- Every implementation target resolves through a fresh native contract graph to one unambiguous owner.
- Implementation and contract evolution are separate operation kinds.
- Successful implementation authorization records the selected task identities together with the exact authorized targets in one atomic operation record.
- Successful authorization creates one atomic operation record with the Git baseline and governing target identities.
- Dirty intended targets require exact verified predecessor provenance before carry-forward.
- An unverified active operation cannot be silently replaced.
- Compact authorization handoff state is derived from current operation evidence and current Git state rather than persisted as another authority artifact.

## Prohibitions

- Path-looking prose must not widen implementation authority.
- Missing task selection must not fall back to authorizing every task in the active change.
- Architectural ownership must not infer implementation-unit membership or widen the selected write set.
- Native contract changes must not authorize implementation writes in the same operation.
- Mutable planning state must not alter historical authorization evidence.
- Reading authorization handoff state must not widen, refresh, or verify an operation.

## Interfaces

- Authorization services produce and persist versioned `OperationRecord` evidence for implementation and contract-evolution operations.
- Implementation operation evidence exposes the explicit selected task identities and resolved authorized targets used for that authorization epoch.
- Authorization services expose a compact read-only handoff projection of the current operation for coordinator and worker transfer.
