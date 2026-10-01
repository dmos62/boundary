# boundary-implement

Use this skill only after an implementation operation has been successfully authorized.

## Establish implementation authority

Before changing project files:

1. Read deterministic Boundary status (`boundary status`) for the current repository.
2. Require an operation to be present with `kind: implementation` and `status: authorized`, and identify its change identity, selected task identities, and exact authorized targets.
3. Treat the selected task identities and authorized targets as the status projection of historical authorization evidence. Do not reconstruct or widen authority from mutable change-system task files.
4. Require the current Git HEAD to match the recorded baseline when a baseline is available. Missing operation evidence, a non-implementation or non-authorized operation, or a stale baseline requires the supported lifecycle transition rather than implementation.
5. Use recorded target-context evidence for handoff orientation, then inspect Boundary effective context for each target before modifying it.

## Procedure

1. Inspect Boundary effective context for each target before modifying it.
2. Preserve every applicable invariant and prohibition, including constraints contributed by broader owning contracts.
3. Use relevant dependency interfaces when the target participates in declared architectural relationships.
4. Modify only targets present in the authorized write set projected by status.
5. Keep implementation work separate from native contract evolution.
6. Run the implementation's normal tests and checks without treating their success as authorization evidence.
7. Finish by running Boundary verification for the active operation.

## Scope expansion

When implementation discovers another required write target:

1. Inspect the target if additional context is useful.
2. Do not write the undeclared target.
3. Finish or otherwise leave the current implementation operation through the supported lifecycle.
4. Add the newly required target to structured change scope.
5. Obtain fresh implementation authorization before writing it.

Previously completed work may be carried into a successor operation only through deterministic predecessor evidence accepted by Boundary.

## Contract conflicts

When requested behavior cannot satisfy the applicable persistent contracts:

1. Stop dependent implementation.
2. Close the current implementation operation through the supported lifecycle.
3. Transition to persistent-contract evolution.
4. Resume implementation only after contract evolution is complete and fresh implementation authorization succeeds.

## Guardrails

- Prompt instructions do not widen authorization.
- The status capsule is query output only; the current product representation is the compact Boundary authorization handoff derived from historical evidence and current repository state.
- A Boundary status handoff is query output derived from historical evidence and current repository state; it does not replace or widen the operation record.
- A previously inspected target is not automatically authorized.
- A target owned by an already represented owner is still undeclared unless it is in the authorized write set.
- Native contract files are not implementation targets.
- Changed planning or task prose cannot retroactively widen the active operation.
- Deterministic authorization and verification findings are authoritative.
