# boundary-contracts

Use this skill for deliberate evolution of persistent Boundary contracts.

## Procedure

1. Identify the durable system rule, ownership statement, applicability rule, or interface that actually needs to change.
2. Confirm that persistent-contract evolution is necessary rather than using it to accommodate an ordinary implementation mistake.
3. Inspect the existing contract graph and relevant effective context before editing contracts.
4. Stop dependent implementation and ensure any active operation is verified before starting another authorization epoch.
5. Authorize the exact native contract files with `boundary contracts authorize --change CHANGE_ID CONTRACT...`.
6. Make the smallest durable contract change that expresses the intended system semantics.
7. Preserve additive applicability: more-specific ownership does not remove broader applicable constraints.
8. Keep ownership and additional applicability explicit.
9. Declare architectural dependencies only when the relationship is durable and useful to downstream target context.
10. Modify only the native contract files authorized for the contract-evolution operation.
11. Run `boundary contracts check` after editing.
12. Run `boundary verify` and require successful closure before dependent implementation begins.
13. Explicitly select the dependent implementation unit and obtain fresh implementation authorization against the resulting canonical graph.

When an ordinary implementation or durable change-system target is unowned, evolve a native contract that explicitly owns the required exact path or durable subtree. The ordinary target is not itself a contract-evolution target and must not be written until contract evolution closes and fresh implementation authorization succeeds.

## Contract design

Prefer:

- narrowly scoped contracts;
- concise invariants and prohibitions;
- explicit ownership;
- explicit additional applicability;
- focused dependency interfaces;
- durable system semantics that future work must preserve.

Avoid:

- repository-wide catch-all contracts;
- implicit override semantics;
- duplicating transient feature intent;
- generated operation facts;
- workflow state;
- rules that merely restate implementation details without durable value.

## Guardrails

- Contract evolution never retroactively authorizes implementation writes.
- `boundary contracts authorize` authorizes only exact native `contracts/**/*.contract.md` targets.
- Do not combine implementation changes with contract changes in one operation.
- Do not auto-own feature, specification, interface-contract, or other change-system paths.
- Do not weaken contracts automatically to make implementation pass.
- Structural validation establishes graph correctness, not semantic correctness of prose.
- Dependent implementation always starts from a fresh authorization epoch.
