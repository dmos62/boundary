# Historical Boundary Material

Status: historical only; not an implementation contract

This directory records context from Boundary's migration history that is useful for repository archaeology but no longer defines supported runtime behavior.

## v0.1 bridge

Boundary began as a Spec Kit × SpecDD integration bridge.

The v0.1 design used:

- Spec Kit as the feature and task system;
- SpecDD `.sdd` files as persistent system specifications;
- a derived feature Change Boundary;
- public `speckit.specdd.*` commands;
- separate context, validation, authorization, and verification stages;
- SpecDD ownership and non-owning modification authority;
- several authorization evidence documents;
- project-wide SpecDD bootstrap state.

That release established several durable lessons that survived the migration:

- feature intent and persistent system constraints need separate authorities;
- implementation write scope must be explicit before authorization;
- operation evidence must be historical rather than recomputed from mutable planning state;
- contract evolution must not retroactively authorize dependent implementation;
- actual writes must be checked against authorization;
- deterministic mechanics should enforce mechanically decidable constraints.

The current Boundary architecture implements those ideas through native contracts, exact structured writes, one atomic operation record, and the `authorize → implement → verify` lifecycle.

The detailed original v0.1 acceptance document was removed from the active documentation set during final migration cleanup. Its complete contents remain available in repository history.

## Agent-instruction exploration

An earlier architecture-exploration document investigated reducing always-loaded framework context, using discoverable skills, deriving effective contract projections, and separating policy, procedure, operation facts, and deterministic enforcement.

Those investigations informed the current design in `spec-agent-instructions.md`.

The exploratory document was intentionally removed from the active documentation set once the resulting architecture became explicit. It should not be treated as a parallel source of requirements.

## Legacy Change Boundary model

The migration runtime once persisted feature-local Change Boundary state and refresh-time effective-context fingerprints.

Native Boundary authorization no longer uses that model.

The former `change-boundary.md` guide was deleted after the supported runtime stopped depending on those artifacts. Repository history remains the source for debugging behavior of revisions that still used them.

## Historical interpretation

When historical material conflicts with current `docs/spec*.md`, current specifications are authoritative.

Historical names, commands, paths, and lifecycle stages must not be reintroduced merely for compatibility unless a current concrete requirement justifies them.
