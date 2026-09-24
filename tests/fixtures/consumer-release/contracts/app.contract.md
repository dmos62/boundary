---
schema: boundary.contract/v1
id: consumer-release-app
owns:
  - src/app.py
applies_to: []
depends_on: []
---

# Consumer Release App

## Purpose

Provide one native project contract in the fresh-clone release fixture.

## Invariants

- Downstream Boundary reconstruction does not require canonical Boundary implementation source in the consumer repository.
