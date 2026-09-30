---
schema: boundary.contract/v1
id: boundary-change-adapter
owns:
  - integration/**
---

# Change-System Adapter Source

## Purpose

Contain concrete change-system integration around native Boundary authorization and verification semantics.

## Invariants

- Change-system integration remains an adapter around provider-neutral Boundary authorization and verification.
- Explicit structured task writes are the only implementation-scope input supplied by the Spec Kit adapter.
- Host-generated state remains separate from canonical Boundary source.
- Planning context is queried on demand rather than persisted as authorization state.
- Implementation entry and exit are the adapter's only blocking Boundary lifecycle transitions.
- Read-only authorization-state queries do not become additional lifecycle transitions or authority sources.

## Prohibitions

- Adapter code must not define Boundary core APIs or native contract semantics.
- Host planning state must not become required native authorization evidence.
- Adapter-specific command names and generated paths must not become Boundary product identities.
- Adapter status queries must not reconstruct or widen authority from mutable host task state.

## Interfaces

- The Spec Kit adapter projects active feature identity and structured task writes into native authorization.
- The Spec Kit adapter classifies its own bookkeeping paths during Git-derived verification.
- The Spec Kit adapter may expose the provider-neutral compact authorization handoff together with its relationship to the active feature.
