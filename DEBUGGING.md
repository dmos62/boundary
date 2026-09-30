# Mise distribution investigation

## Objective

Prove the downstream mise mechanism before changing Boundary's normative distribution specifications.

The required mechanism must:

- install a real `boundary` command from Boundary source;
- select an explicit committed Git revision rather than the source checkout's current `HEAD`;
- reproduce the selected revision with `mise install --locked`;
- fail closed for unavailable revisions and incomplete locks;
- remain unaffected by unrelated dirty working-tree bytes when an exact committed revision is selected;
- keep operator-local source paths out of committed project state;
- retain the required Python dependency resolution without introducing another Boundary-owned revision lock.

## Starting state

The supplied harness reports mise 2026.9.12.

There is currently no tracked `mise.toml`, `mise.lock`, `pyproject.toml`, or `uv.lock`.

Boundary is currently invoked from source rather than installed as a conventional Python console application.

## Upstream-behavior warning

Current mise documentation describes `pypi:` Git sources as version-only locked even when uv-backed Python dependency graph locking is available for ordinary PyPI packages.

Current documentation also states that full Python dependency graph locking requires uv 0.12.10 or newer.

Those current docs are useful design evidence but are not proof of behavior for the supported mise 2026.9.12 installation. The harness probe must establish actual behavior before any distribution specification is rewritten.

In particular, a successful `pypi:git+file://...` install is not sufficient by itself. The mechanism is unsuitable if either:

- the absolute operator source path leaks into portable `mise.toml` or `mise.lock`; or
- the resulting lock only retains a top-level Git revision while re-resolving Python dependencies.

## Active probe

`dev-scripts.include` now creates a disposable local Git repository containing a minimal Python `boundary` console script with two commits.

It probes:

1. direct `pypi:git+file://...` configuration pinned to the first commit while the source checkout is at the second commit;
2. locked installation and execution of that requested commit;
3. a fresh locked installation after dirtying the source checkout;
4. an empty/incomplete `mise.lock`;
5. a nonexistent 40-character revision;
6. an operator-local `[tool_alias]` mapping where committed project configuration uses only the logical `boundary` tool name;
7. whether either committed lock form contains the absolute local repository path;
8. whether mise emits a Python dependency-lock sidecar.

## Interpretation

If direct local Git installation fails on mise 2026.9.12, do not document it as supported merely because a newer mise release accepts more Git URL forms.

If direct local Git works but embeds the absolute source path in project state, it does not satisfy Boundary's portability requirement.

If an operator-local backend alias works and leaves both project configuration and `mise.lock` path-free, it is a candidate source-supply boundary. It still must satisfy dependency locking.

If Git-backed `pypi:` remains version-only, do not weaken the TODO requirement silently. Investigate another mise-native arrangement that can represent both the exact Boundary source revision and frozen Python dependencies, or explicitly revise the target architecture only after establishing why the original requirement is impossible or unnecessary.

Delete this file when the distribution mechanism is proven and the durable conclusions have moved into the focused specifications.
