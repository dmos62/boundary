---
schema: boundary.contract/v1
id: boundary-agent-adapters
owns:
  - adapters/**
---

# Legacy Agent Adapters

## Purpose

Own removal of the deprecated runtime-specific materializers.

## Invariants

- No agent-specific adapter remains after the agent-neutral delivery migration.
