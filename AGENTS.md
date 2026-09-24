Before working on this project, read `docs/spec.md` and the focused specification documents relevant to the area being changed.

Treat `docs/spec*.md` and native contracts under `contracts/` as source-adjacent development contracts, not optional documentation. Applicable native contracts are additive.

For implementation work:

- derive write scope only from explicit structured writes supplied by the active change-system adapter;
- inspect effective Boundary context for targets rather than manually reproducing contract resolution;
- use the `authorize → implement → verify` lifecycle;
- do not modify undeclared targets under an active implementation operation;
- stop and perform an explicit scope-expansion transition before adding newly discovered write targets;
- keep persistent-contract evolution separate from implementation and require fresh implementation authorization afterward;
- treat deterministic Boundary authorization and verification as authoritative.

Do not use generated `.agents/` or `.specify/` material as canonical source. Canonical procedure lives under `skills/`, concrete integrations under `adapters/` and `integration/`, and persistent project semantics under `contracts/`.

Historical migration material does not define current Boundary behavior.
