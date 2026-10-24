# Boundary Development Setup

The source checkout uses mise for Python and uv. Run `mise install`, then `mise run bootstrap` to install the checkout into the development environment and materialize Boundary agent skills. There is no planning-system prerequisite.

Use `mise run contracts-check`, `mise run test-distribution`, and `mise run test` for validation. The installed `boundary` executable is the same public CLI consumed by downstream repositories.

Current specifications and native contracts are source-adjacent development authority. The `pre-change → post-change` lifecycle applies to implementation work, and contract evolution uses its own pre-change operation. Resolve any old-format operation before switching the worktree to a new Boundary binary.
