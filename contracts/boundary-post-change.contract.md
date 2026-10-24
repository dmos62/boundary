---
schema: boundary.contract/v1
id: boundary-post-change
owns:
  - src/boundary/post_change/**
depends_on:
  - boundary-pre-change
  - boundary-context
  - boundary-native-contracts
---

# Post-change and Abandonment

## Purpose

Check actual Git writes against an open operation or close it explicitly without verification.

## Invariants

- Post-change compares actual index and worktree state with the stored pre-change baseline.
- Git `HEAD` must remain unchanged and every actual write must fit the exact allowed scope.
- Implementation targets retain their historical effective contract context.
- Successful post-change stores exact verified final states; failure leaves the operation open.
- Post-abandon records an unverified `abandoned` outcome and preserves project files.

## Prohibitions

- Neither closing transition commits, resets, restores, or rebases project files.
- Planning or generated paths receive no implicit actual-write exemption.
- Contract evolution cannot retroactively authorize implementation.
