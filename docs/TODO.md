# TODO

## Finish Linux Spec Kit script-mode rollout

The script-mode implementation and project-state ownership decision are complete.

Pinned Spec Kit 1.0.10 remains responsible for its project-state policy. Boundary accepts the stock managed `.specify/.gitignore`, keeps persistent and shareable Spec Kit state visible, excludes only Boundary-owned generated paths locally, and treats inactive script variants retained after a mode transition as non-authoritative host-generated residue.

Remaining work is regression evidence:

- Extend the real pinned-CLI Linux `ps` to `sh` recovery coverage to assert the ownership boundary explicitly.
- Confirm persistent and shareable Spec Kit changes remain visible after recovery, including integration metadata, registries, the active Bash scripts, and materialized core `speckit-*` skills.
- Confirm Boundary-owned generated runtime and adapter paths remain absent from normal downstream Git status.
- Confirm the stock `.specify/.gitignore` remains host-managed and does not hide shared `.specify/` state.
- Confirm the retained inactive `.specify/scripts/powershell/` tree is not selected, modified, or deleted by Boundary during recovery.
- Retain clean-consumer coverage for the managed Boundary local exclusion block.
- Run contract checks, consumer tests, script-mode tests, and real pinned-CLI Linux coverage. Remove this TODO when those regression checks pass.
