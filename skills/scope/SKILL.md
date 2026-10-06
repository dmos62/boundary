# boundary-scope

Use this skill while planning implementation work or refining implementation tasks.

## Procedure

1. Start from the active change system's requested work and structured task state.
2. Separate ordinary implementation from persistent-contract evolution before declaring writes.
3. Identify the exact repository-relative targets the implementation intends to modify.
4. Include durable project or workflow records when implementation is expected to modify them, unless the active change system genuinely owns those paths as bookkeeping.
5. Inspect Boundary effective context for each candidate target.
6. Confirm that every implementation target has one unambiguous primary owner.
7. Read the applicable invariants, prohibitions, and relevant dependency interfaces returned for each target.
8. Treat all applicable contracts additively, including broader owning contracts that continue to constrain a more specifically owned target.
9. Record the exact implementation writes through the active change system's structured write declaration.
10. For follow-up work on a path already declared by an active-change task, refine or reopen that owning task outside any active implementation operation; do not append another task that declares the same path.
11. After follow-up refinement, rerun declared-scope readiness as needed and hand off the owning task for fresh explicit selection and implementation authorization.
12. Prefer owner-local tasks when the work separates cleanly without harming coherence.
13. Keep coordinated multi-owner work together when that is the clearer implementation unit.
14. After structured writes are complete, use the change-system integration's declared-scope readiness preflight over the complete declared write projection.
15. Resolve invalid, unowned, or ambiguous declared targets before implementation entry.
16. Re-inspect targets when planning changes enough that the intended write set or relevant relationships change.

## Guardrails

- Path-looking prose is advisory context, not implementation authority.
- Exploratory targets do not belong in the declared write set unless implementation is expected to modify them.
- Durable checkpoints, continuation records, feedback records, and similar project artifacts are ordinary writes unless the active change system explicitly owns them.
- One implementation path must remain declared by only one task within the active change; follow-up work does not justify duplicate structured write ownership.
- Do not invent persistent contracts or bookkeeping classification merely to make declared-scope readiness pass.
- Declared-scope readiness preflight is non-authorizing: it creates no operation record, captures no Git authorization baseline, selects no implementation unit, and grants no write authority.
- Do not infer permission from an owner name, nearby file, similar task, preflight result, or previous operation.
- Do not authorize implementation from this skill.
- Do not mix native contract edits with implementation writes.
- Do not create a persisted planning projection merely to cache effective context.

## Handoff

Implementation-ready scope has exact declared writes, a clean declared-scope readiness preflight, and enough inspected effective context to explain why those targets are coherent.

Authorization remains a separate deterministic transition performed against fresh canonical contracts, the explicitly selected implementation unit, and current repository state.

Successful Boundary verification proves only that an operation complied with its authorized write scope. Feature completion, feature correctness, and live acceptance remain separate concerns.
