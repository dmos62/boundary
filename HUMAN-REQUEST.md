# Human request: choose the mise distribution tradeoff

Boundary's current downstream distribution requirements cannot all be satisfied by the mise-native Python mechanisms tested under mise 2026.9.12 and uv 0.12.17.

The corrected ordinary-PyPI bridge successfully locked an exact commit-derived Boundary version and a nontrivial Python dependency graph. The generated native `uv.lock`, however, persisted both the disposable registry address and wheel artifact URLs. In the probe those values were `http://127.0.0.1:<ephemeral-port>/...`.

That is actual lock output, not only source-code inference. It violates the requirement that portable committed state contain no ephemeral registry or service locator.

The other plausible mise-native family has the opposite tradeoff: Git-backed Python tools preserve source identity, but mise does not give them the native frozen uv dependency sidecar used by ordinary PyPI tools.

The later `mise install --locked` probe also encountered a Python shim problem after mise-state isolation. That fixture issue does not need to be resolved before this decision because the generated lock state had already failed the portability criterion.

Please choose which requirement should change before the normative distribution specifications are rewritten.

Possible directions are:

1. Require a stable package registry/artifact service.
   Local Git may remain the source from which an exact commit-derived artifact is built, but that artifact must be published to a stable registry before mise locking. Native mise/uv dependency locking and portable committed state are retained, at the cost of requiring distribution infrastructure rather than a disposable operator-local bridge.

2. Use mise's Git-backed Python installation and relax the frozen transitive-dependency requirement.
   Exact Git source identity remains native to the installation model and no package-service locator is needed, but `mise.lock` does not carry the same native frozen Python dependency graph as the PyPI backend.

3. Permit the native lock state to contain the package/index locator.
   The ordinary-PyPI bridge can retain its dependency graph, but downstream reproducibility then depends on the recorded service/artifact URLs remaining reachable. An ephemeral localhost bridge would not be portable, so this choice must define what locator lifetime and availability are acceptable.

4. Reverse the prohibition on an additional Boundary-owned lock or non-mise dependency-lock procedure.
   This could preserve more of the current requirements, but it abandons the stated goal that mise configuration plus `mise.lock` be the only revision/dependency lock state.

Do not rewrite the normative distribution architecture until one of these directions, or another explicit requirement change, is selected.
