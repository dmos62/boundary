---
schema: boundary.contract/v1
id: boundary-request
owns:
  - src/boundary/request/**
---

# Generic Change Request

## Purpose

Decode a versioned planning-system-neutral task projection for pre-change.

## Invariants

- The request contains an opaque change ID, ordered task IDs and exact writes, and explicit selected task IDs.
- Invalid, duplicate, unknown, or empty selected scope fails before baseline capture.
- Request field validation is strict; path syntax is canonical and repository-relative.

## Prohibitions

- Boundary must not parse a particular planning system's files or infer writes from prose.
- Omitted selection must not mean all tasks.
- Request parsing must not grant authority apart from a successful pre-change record.
