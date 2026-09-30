# Change-System Adapter Architecture

Boundary treats a change system as an adapter that supplies structured implementation intent and lifecycle integration.

The adapter contract is provider-neutral. Host-specific workflow names, feature files, command names, constitution concepts, and generated layouts do not belong in Boundary core.

## Responsibilities

A change-system adapter supplies:

- the active change identity;
- stable task identities and task order;
- exact implementation writes declared by each task;
- explicit implementation-unit task selection at authorization entry;
- adapter-owned feature or generated paths;
- implementation lifecycle entry and exit integration.

Boundary supplies native contract discovery and effective context, implementation-unit authorization, operation records and epochs, Git baselines and actual-write derivation, contract-evolution separation, and implementation verification.

An adapter translates host state. It does not decide whether an implementation write is authorized.

## Active change identity

The adapter exposes one opaque, non-empty change ID that remains stable while Boundary authorization and verification refer to the logical change.

A host may use a directory name, database identifier, branch-associated record, or another native identity internally. Boundary does not interpret that representation.

## Task scope and explicit writes

The adapter projects implementation tasks as an ordered sequence. Each task contains one opaque, non-empty task ID and zero or more exact repository-relative implementation write paths.

Task IDs must be unique within the active change. Task order is preserved for diagnostics, unit selection, and historical evidence.

Boundary does not infer writes from descriptive prose, path-shaped text, headings, or owner names. The adapter must use the host's structured write declaration mechanism.

The change-level write projection is the deterministic ordered union of task writes, preserving first occurrence. It is useful for planning and diagnostics but is not implementation authority.

A path declared by more than one task is ambiguous structured scope and must be rejected. A declared write expresses intent only; authorization still resolves selected targets against fresh contracts and repository state.

## Declared-scope preflight

After structured task writes exist, an integration may run a non-authorizing preflight over the complete change-level ordered write projection.

The preflight uses Boundary target inspection rather than reproducing contract resolution. It may surface invalid targets, missing ownership, or ambiguous ownership before implementation entry.

This diagnostic:

- creates no operation record or Git authorization baseline;
- does not select or infer an implementation unit;
- grants no authority to writes from unselected tasks;
- does not replace fresh target resolution during authorization;
- must not be persisted as a feature-local authorization artifact.

A host may require a clean preflight before its tasks are implementation-ready without changing Boundary authorization semantics.

Durable workflow records are ordinary writes unless the host genuinely owns them as bookkeeping. If implementation must update a checkpoint, continuation record, feedback record, or similar artifact, task generation must declare the exact path so preflight can inspect its ownership.

## Implementation-unit selection

An implementation unit is an explicit selection of one or more task IDs from the active change.

The adapter rejects missing, unknown, or duplicate task IDs and selections whose structured write set is empty. Selected tasks are projected in canonical host order; their write set is the deterministic ordered union preserving task path order.

Unselected tasks grant no write authority, even when they belong to the same change or owner. Selecting every task is valid only when every task ID is explicit.

Boundary resolves ownership and effective contract context after selection. A unit may span one or several owners; ownership informs evidence and diagnostics but does not alter the selected write set.

The operation record, not a persistent unit file, is the historical identity of the authorized unit. It stores selected task IDs, selected task evidence, and resolved targets.

## Adapter-owned paths

The adapter may identify deterministic repository-relative paths belonging to change-system bookkeeping rather than product implementation.

Adapter-owned classification must not:

- hide a path in the selected unit's declared implementation write set;
- hide a native Boundary contract;
- convert an unauthorized implementation write into generated state;
- depend on task prose or on whether verification would otherwise fail.

Boundary may exclude valid adapter-owned state from actual-write diagnostics while continuing to verify declared targets normally. Durable project workflow records not owned by the host remain ordinary writes.

## Implementation lifecycle

Boundary recognizes two structural integration points for ordinary implementation.

### Entry

The adapter supplies a fresh normalized change projection plus explicit task selection. Boundary authorization evaluates the active change, selected tasks, their exact writes, canonical target context, current Git state, and applicable predecessor evidence.

Implementation begins only after successful authorization records an operation. Planning and preflight are never reused as authorization evidence.

### Exit

Boundary verifies repository state against the active historical operation. The adapter must ensure the operation belongs to the same host change before closure.

Verification stays scoped to the current unit, accounts for valid adapter-owned state, and is not replaced by ordinary tests or host workflow completion.

## Authorization-state handoff

An adapter may expose Boundary's compact current authorization handoff for coordinators and workers.

The handoff is read-only query output derived from current operation evidence and current Git `HEAD`. The adapter must not reconstruct task authority from mutable host state.

An adapter may report whether the handoff's `changeId` matches its active host change. Reading the handoff requires no task selection and creates no operation evidence.

## Scope expansion

When implementation discovers an additional required write:

1. the active operation does not gain permission;
2. leave implementation through the supported Boundary lifecycle;
3. update host structured task scope if the target was undeclared;
4. explicitly include an existing task if the target belonged to an unselected task;
5. provide a fresh projection and explicit next-unit selection;
6. require fresh Boundary authorization.

Verified predecessor work may carry forward only through deterministic predecessor evidence. Same-owner and cross-owner discoveries may produce different diagnostics but never different authorization requirements.

## Contract evolution

Persistent contract evolution is separate from implementation scope. A contract-evolution operation modifies only native Boundary contract files.

Changing host task scope or selection does not authorize contract edits. After contract evolution, dependent implementation requires a fresh projection, explicit unit selection, and fresh authorization.

## On-demand context

Target inspection is a Boundary query, not change-system lifecycle state.

Planning tools may invoke `boundary inspect <target...>` whenever context is needed, including declared-scope preflight. Adapters should not persist a context phase or copy canonical contract semantics into host feature artifacts.

## Concrete Spec Kit adapter

The Spec Kit adapter uses the active feature directory name as its opaque change identity and preserves task order from `tasks.md`.

Implementation writes come only from dedicated indented `Writes:` metadata attached directly to checklist tasks. Backticked repository-relative paths in that metadata are exact writes; path-looking prose elsewhere is not authority input.

Malformed, empty, duplicate, or ambiguously repeated structured write declarations are blocking adapter errors. Task refinement must include durable project records in `Writes:` metadata whenever implementation is expected to update them.

After task refinement, the integration should inspect the deterministic ordered union of declared writes through Boundary target inspection. Ownership defects are therefore reported before implementation entry when possible, but this remains non-authorizing.

Implementation authorization requires explicit task IDs. Direct invocation accepts repeated `--task` arguments; the workflow overlay transports the same input through transient `BOUNDARY_TASK_IDS` JSON.

`BOUNDARY_TASK_IDS` is transport only. It is not persistent project state or operation evidence. No selection means no authorization, not the complete feature.

The adapter's non-blocking `status` query returns Boundary's compact authorization handoff plus whether its change identity matches the active feature. It neither selects tasks nor authorizes or verifies writes.

The adapter is installed under Spec Kit extension identity `boundary`, yielding public wrappers `speckit.boundary.authorize` and `speckit.boundary.verify`. Those wrappers invoke native Boundary transitions; they are adapter commands, not product identities.

The workflow overlay owns the blocking authorization and verification transitions and never reconstructs feature-wide scope. Planning and task refinement use `boundary inspect` on demand. There is no persisted context phase or public validation phase, and extension hooks do not duplicate the overlay gates.

Spec Kit feature artifacts and `.specify/` state are adapter-owned for actual-write classification unless a path is an authorized implementation target or native Boundary contract.

## Core isolation

Boundary core must not depend on host feature directory names, task document syntax, workflow stages, command namespaces, constitutions, extension or overlay concepts, or generated agent discovery paths.

Replacing the change system should require a new adapter, not changes to native contracts, authorization, agent procedure, or verification semantics.

## Determinism

Given the same host change state and explicit task selection, the adapter must produce the same normalized unit. Projection must not depend on transient agent conversation state.

Authorization and verification consume fresh host state at their lifecycle transitions. Verification remains bound to historical operation evidence even if host tasks later change.

Declared-scope preflight is recomputed from current structured host state and remains advisory.

## Failure behavior

Malformed or ambiguous structured change state is blocking.

Missing change identity or selection, unknown or duplicate selected tasks, duplicate task identities, repeated write ownership between tasks, invalid write paths, empty selected-unit writes, or invalid adapter-owned path declarations must not become permissive defaults.

When required scope cannot be represented, implementation remains unauthorized until host state or explicit selection is corrected. Preflight may also identify ownership defects elsewhere in the declared change without enlarging the selected unit or creating historical evidence.
