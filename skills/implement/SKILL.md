# boundary-implement

Use this skill only after an implementation operation has been successfully authorized.

## Establish implementation authority

Before changing project files:

1. Run `boundary inspect --authorized` for the current repository.
2. Require the query to establish a current operation with `kind: implementation`, `status: authorized`, and a Git `HEAD` matching its authorization baseline.
3. Treat the selected task identities and exact target set shown by that query as projections of historical authorization evidence. Do not reconstruct or widen authority from mutable change-system task files.
4. Read the freshly resolved effective Boundary context for every authorized target before modifying it.
5. If authorized-unit inspection reports missing operation evidence, the wrong operation kind or status, or a stale baseline, use the supported lifecycle transition rather than implementation.

`boundary status` is a recovery, handoff, and debugging query. It is not an additional routine prerequisite after `boundary inspect --authorized`.

## Procedure

1. Preserve every applicable invariant and prohibition shown for the authorized targets, including constraints contributed by broader owning contracts.
2. Use relevant dependency interfaces when a target participates in declared architectural relationships.
3. Modify only targets present in the authorized write set.
4. Keep implementation work separate from native contract evolution.
5. Run the implementation's ordinary tests and checks without treating their success as authorization evidence.
6. Finish by running `boundary verify` for the active operation.

## Scope expansion

When implementation discovers another required write target:

1. Use `boundary inspect <target>` if additional context is useful.
2. Do not write the undeclared target.
3. Finish or otherwise leave the current implementation operation through the supported lifecycle.
4. If the target is not already declared, refine structured change scope outside the active implementation operation.
5. If follow-up work returns to a path already declared by an existing task, refine or reopen that owning task rather than adding a second task with duplicate write ownership.
6. Obtain fresh explicit task selection and implementation authorization before writing the target.

Previously completed work may be carried into a successor operation only through deterministic predecessor evidence accepted by Boundary.

## Contract conflicts

When requested behavior cannot satisfy the applicable persistent contracts:

1. Stop dependent implementation.
2. Close the current implementation operation through the supported lifecycle.
3. Transition to persistent-contract evolution.
4. Resume implementation only after contract evolution is complete and fresh implementation authorization succeeds.

## Guardrails

- Prompt instructions do not widen authorization.
- Authorized-unit inspection is read-only query output derived from historical operation evidence plus fresh contract context; it does not replace or widen the operation record.
- A previously inspected target is not automatically authorized.
- A target owned by an already represented owner is still undeclared unless it is in the authorized write set.
- Native contract files are not implementation targets.
- Changed planning or task prose cannot retroactively widen the active operation.
- Successful verification closes the authorized scope epoch but does not establish feature correctness, completion, or live acceptance.
- Deterministic authorization and verification findings are authoritative.
