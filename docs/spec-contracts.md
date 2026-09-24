# Native Contract Semantics

Boundary uses a native persistent-contract model for deterministic scope resolution and concise progressive agent context. It preserves hierarchical constraints without inheriting filesystem-position semantics or project-wide provider bootstrap rules.

## Canonical location

Native contracts live under:

    contracts/**/*.contract.md

A contract file's directory has no semantic meaning. Moving a contract file without changing its ID or declared scopes must not change which implementation targets it governs.

## Contract form

Boundary v1 uses Markdown with YAML frontmatter.

Example:

    ---
    schema: boundary.contract/v1
    id: payments

    owns:
      - src/payments/**

    applies_to:
      - src/api/payment-methods/**

    depends_on:
      - users
    ---

    # Payments

    ## Purpose

    Own payment processing and payment-provider integration.

    ## Invariants

    - Raw card data is never persisted.
    - Provider-specific details remain behind the payment-provider interface.

    ## Prohibitions

    - Payment code must not depend on user persistence internals.

    ## Interfaces

    - Consumers use the public payment-provider interface.

Only frontmatter carries deterministic scope and graph semantics. Markdown sections carry human-readable architectural intent.

## Required fields

Every contract has `schema` and a stable `id`. A contract must also declare at least one of `owns` or `applies_to`, both arrays of explicit repository scopes. Optional `depends_on` contains contract IDs.

Boundary v1 has no `extends`, `override`, `except`, delegated-write, or equivalent permission field.

## Path scope grammar

Boundary v1 supports only:

- an exact repository-relative path;
- a subtree path ending in `/**`.

Examples:

    src/auth/service.ts
    src/auth/**
    docs/api/**

The following are invalid Boundary v1 scope syntax:

    **
    src/*/service.ts
    src/{auth,users}/**
    src/**/generated/*.ts

This restricted grammar keeps intended-target behavior independent of filesystem existence and makes containment mechanically decidable. Exact paths are always exact. Subtree paths always denote the subtree even when the directory does not yet exist. No probe file or external resolver is needed.

## No global catch-all contract

Boundary v1 does not support a repository-wide catch-all scope; `**` is invalid.

Cross-component or cross-layer constraints must name concrete scopes. Development-process rules that truly apply to every change belong in change-system governance or stable Boundary procedure, not in a global persistent architecture prompt.

## Applicability

A contract applies to every target matched by one of its `owns` or `applies_to` scopes. All matching contracts apply additively. There is no nearest-contract-wins rule, and a more-specific contract cannot erase a broader matching contract by omission.

## Nested ownership

Ownership may be nested when scopes are strictly contained:

    payments owns src/payments/**
    stripe owns src/payments/providers/stripe/**

For `src/payments/providers/stripe/client.ts`, `stripe` is the primary owner, while both `payments` and `stripe` remain applicable because both ownership scopes match.

The effective context therefore contains broader Payments constraints plus more-specific Stripe constraints. This preserves hierarchical constraint propagation without coupling semantics to contract-file placement.

## Ownership ambiguity

A target must have one unambiguous most-specific owner. With the restricted v1 path grammar, ownership scopes can be compared structurally.

The graph is invalid when matching ownership scopes overlap without one being strictly more specific than the other, or when equally specific scopes claim the same target. Authorization fails for an unowned or ambiguously owned implementation target.

## No override semantics in v1

Applicable contract semantics are monotonic. More-specific contracts may add requirements but cannot cancel broader requirements.

If a broad rule is no longer correct for a subtree, contract evolution must deliberately change the contract structure or narrow the original scope. Boundary v1 has no exception mechanism.

## Cross-component contracts

Boundary does not use a global cross-contract file. A durable relationship spanning components may use a narrowly scoped relationship contract:

    ---
    schema: boundary.contract/v1
    id: auth-user-identity

    applies_to:
      - src/auth/**
      - src/users/identity.ts

    depends_on:
      - auth
      - users
    ---

Such a contract has no ownership role unless it also declares `owns`. Its prose should describe only the durable relationship. Explicit applicability keeps it out of unrelated target context.

## Dependencies

`depends_on` identifies architectural dependencies between contract IDs.

For normal target context, Boundary exposes the depended-on contract's `Interfaces` section and source provenance rather than importing all of its internal invariants. If a rule from another component must directly constrain a caller, represent it through explicit `applies_to` scope or a dedicated relationship contract.

This avoids accidental transitive expansion of agent context.

## Semantic sections

Boundary v1 recognizes these conventional Markdown sections:

- `Purpose`;
- `Invariants`;
- `Prohibitions`;
- `Interfaces`.

The engine may preserve other sections for raw inspection, but only recognized sections participate in standard effective-context projection. Boundary does not attempt to prove arbitrary prose mechanically: structure determines relevance, and prose explains meaning.

## Effective target context

For target `T`, Boundary derives:

1. the most-specific unambiguous owner;
2. every contract whose `owns` or `applies_to` scope matches `T`;
3. recognized semantic sections from those contracts;
4. relevant `Interfaces` sections from directly declared dependencies;
5. exact source provenance and content identities.

Collections are normalized and ordered deterministically. The result is disposable query output, not another persistent contract representation or feature artifact.

## Structural validation

`boundary contracts check` must deterministically validate at least:

- frontmatter syntax and schema version;
- unique contract IDs;
- canonical repository-relative scopes;
- allowed scope grammar and prohibition of catch-all `**`;
- ownership nesting and ambiguity;
- existence of declared dependency IDs;
- dependency self-reference;
- deterministic contract discovery;
- recognized section extraction.

Additional checks should be added only when their semantics are precise.

## Deliberately omitted v1 concepts

Boundary v1 does not preserve legacy provider concepts automatically, including:

- project-wide framework bootstrap inheritance;
- directory-position semantics;
- arbitrary ownership glob syntax;
- delegated non-owner write permissions;
- task entries inside persistent contracts;
- global root-contract inheritance;
- provider framework versions.

If a concrete Boundary use case later requires delegated non-owner write permission, introduce it as a native owner-issued concept rather than inheriting compatibility behavior.
