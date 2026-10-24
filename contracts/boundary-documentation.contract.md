---
schema: boundary.contract/v1
id: boundary-documentation
owns:
  - README.md
  - docs/**
---

# Boundary Documentation

## Purpose

Explain the current generic CLI, persistent contracts, operation lifecycle, and downstream setup.

## Invariants

- Current instructions use pre-change, post-change, and post-abandon naming.
- Upgrade guidance requires resolving old operations and manual cleanup of legacy Git-metadata state.
- Historical provider material is clearly separate from current behavior.
