# Change-System Adapter Architecture

Boundary treats a change system as an adapter that supplies structured implementation intent and lifecycle integration.

The adapter contract is provider-neutral. Host-specific workflow names, feature file names, command names, constitution concepts, and generated directory layouts do not belong in Boundary core.

## Responsibilities

A change-system adapter supplies:

- the active change identity;
- stable task identities and task order;
- exact implementation writes declared by each task;
- an explicit implementation-unit task selection at authorization entry;
- adapter-owned feature or generated paths;
- implementation lifecycle entry and exit integration.

Boundary supplies:

- native contract discovery and effective context;
- implementation-unit authorization;
- operation records and authorization epochs;
- Git baselines and actual-write derivation;
- contract-evolution separation;
- implementation verification.

An adapter translates host state. It does not decide whether an implementation write is authorized.

## Active change identity

The adapter exposes one opaque, non-empty change ID for the active change.

Boundary does not interpret the ID's syntax and does not derive product semantics from it.

The ID must remain stable for the logical change while implementation authorization and verification refer to that change.

A host may use a directory name, database identifier, branch-associated record, or another native identity internally. That representation remains adapter-specific.

## Task scope

The adapter projects implementation tasks as an ordered sequence.

Each task contains:

- one opaque, non-empty task ID;
- zero or more exact repository-relative implementation write paths.

Task IDs must be unique within the active change.

Task order is preserved because diagnostics, implementation-unit selection, and authorization evidence refer back to the host's task order.

Boundary does not infer writes from descriptive prose, path-shaped text, headings, or owner names.

The adapter must use the host's structured write declaration mechanism.

## Explicit writes

Implementation writes are exact repository-relative paths.

The change-level write projection is the deterministic ordered union of task writes, preserving first occurrence. That union is useful for planning and diagnostics but is not itself implementation authority.

A path declared by more than one task is ambiguous structured scope and must be rejected rather than silently normalized into a different task model.

A declared write expresses implementation intent only. It does not itself grant permission.

Boundary authorization resolves the selected unit's declared targets against fresh canonical contracts and current repository state.

## Declared-scope preflight

After structured task writes exist, a change-system integration may run a non-authorizing preflight over the complete change-level ordered write projection.

The preflight uses Boundary's effective target inspection rather than reimplementing contract resolution in the adapter. Its purpose is to surface scope defects such as invalid targets, missing ownership, or ambiguous ownership before an implementation unit begins.

This diagnostic:

- is planning or task-readiness information, not authorization evidence;
- creates no operation record and captures no Git authorization baseline;
- does not select tasks or infer an implementation unit;
- does not grant authority to writes from unselected tasks;
- does not replace fresh target resolution during later authorization;
- must not be persisted as a feature-local authorization artifact.

A host workflow may require declared-scope diagnostics to be clean before treating its task set as implementation-ready. That host readiness rule does not change Boundary core authorization semantics: authorization still consumes only the explicitly selected tasks and independently reloads current contracts and Git state.

Durable project workflow records are ordinary writes unless the host change system genuinely owns them as bookkeeping. When implementation is expected to update a checkpoint, continuation record, feedback record, or similar project artifact, task generation must represent that exact path in structured write metadata so the preflight can inspect its real ownership before implementation.

## Implementation-unit selection

An implementation unit is an explicit selection of one or more task IDs from the active change.

The adapter validates the supplied identities against the fresh ordered task projection. It must reject:

- a missing selection;
- unknown task IDs;
- duplicate task IDs;
- a selection whose resulting structured write set is empty.

Selected tasks are projected in canonical host task order. The unit write set is their deterministic ordered union, preserving each task's declared path order.

Tasks not selected for the unit contribute no write authority, even when they belong to the same active change or primary owner.

Selecting every task is valid only when every task ID is explicitly selected. The adapter must not silently treat an omitted selection as "all tasks."

Boundary resolves primary ownership and effective contract context after unit selection. The selected unit may resolve to one owner or several owners. Owner resolution informs authorization evidence and diagnostics but does not alter the selected write set.

The operation record, not a new persistent unit file, is the historical identity of the authorized implementation unit. It records the selected task IDs together with the selected task evidence and resolved authorized targets.

## Adapter-owned paths

The adapter may identify paths that belong to change-system bookkeeping rather than product implementation.

Examples include host-owned feature state or generated lifecycle artifacts.

Adapter-owned path rules must be deterministic and repository-relative. They may use exact paths or explicitly declared subtrees when the host owns an entire generated subtree.

Adapter-owned classification must not:

- hide a path that is in the active unit's declared implementation write set;
- hide a native Boundary contract write;
- convert an otherwise unauthorized implementation write into generated state;
- depend on free-form task prose;
- depend on whether verification would otherwise fail.

Boundary may exclude valid adapter-owned state from implementation actual-write diagnostics while continuing to verify declared implementation targets normally.

The concrete path vocabulary remains in the adapter. Boundary core receives only the normalized classification.

Durable project workflow records that are not owned by the host change system remain ordinary writes. They require explicit task declaration and native contract ownership rather than adapter-owned masking.

## Implementation lifecycle

Boundary recognizes two structural integration points for ordinary implementation.

### Entry

At implementation entry, the adapter supplies a fresh normalized change projection plus the explicit task selection for the requested implementation unit.

Boundary authorization then evaluates:

- active change identity;
- selected task identities in host order;
- exact declared writes belonging to those selected tasks;
- canonical target context;
- current Git state;
- predecessor evidence when applicable.

Implementation may begin only after Boundary records a successful authorization operation.

Planning-time inspection, including declared-scope preflight, is not an authorization transition and is never reused as authorization evidence.

### Exit

At implementation exit, Boundary verifies the active operation from repository state.

Verification derives actual writes from Git and compares them with the immutable authorized write set while accounting for valid adapter-owned state.

The adapter must ensure that the active Boundary operation belongs to the same host change before requesting closure.

The adapter does not widen verification from the current unit back to the whole change.

The adapter may allow its host workflow to continue only after the Boundary verification transition returns its result.

Ordinary tests and host workflow completion do not substitute for Boundary verification.

## Authorization-state handoff

An adapter may expose Boundary's compact current authorization handoff as a read-only convenience for coordinators and workers.

The handoff is not another lifecycle transition. It is derived from current Boundary operation evidence and current Git `HEAD`; the adapter must not reconstruct task authority from mutable host state.

An adapter may report whether the handoff's `changeId` matches its currently active host change. That relationship is informational and does not alter either the historical operation or host task state.

No task selection is required to read the handoff, and reading it creates no operation evidence.

## Scope expansion

When implementation discovers an additional required write:

1. the active implementation operation does not gain permission implicitly;
2. the current operation must leave implementation through the supported Boundary lifecycle;
3. if the target is undeclared, the adapter updates structured task scope in its own change system;
4. if the target belongs to an unselected existing task, the next unit selection explicitly includes that task;
5. Boundary receives a fresh normalized change projection and explicit unit selection;
6. fresh implementation authorization is required.

Previous verified work may carry forward only through Boundary's deterministic predecessor evidence.

Boundary may report whether the newly requested target has the same primary owner as the previous unit or crosses an owner boundary. That distinction may guide coordination, but it never changes the authorization requirement.

## Contract evolution

Persistent contract evolution is separate from implementation scope supplied by a change adapter.

A contract-evolution operation modifies only native Boundary contract files.

Changing host task scope or unit selection does not authorize contract edits.

After contract evolution completes, dependent implementation requires a fresh adapter projection, explicit unit selection, and fresh Boundary implementation authorization.

## On-demand context

Target inspection is a Boundary query, not a change-system lifecycle state.

Planning tools may invoke `boundary inspect <target...>` whenever target context is needed, including a declared-scope preflight over the ordered union of structured task writes.

Adapters should not create a persisted context phase or copy canonical contract semantics into host feature artifacts merely to make them available to agents.

## Concrete Spec Kit adapter

The Spec Kit adapter uses the active feature directory name as its opaque change identity and preserves task order from `tasks.md`.

Implementation write declarations come only from dedicated indented `Writes:` metadata attached directly to checklist tasks. Backticked repository-relative paths in that metadata are projected as exact writes. Incidental path-looking prose elsewhere in a task is not authorization input.

Malformed, empty, duplicate, or ambiguously repeated structured write declarations are blocking adapter errors.

Spec Kit task refinement must include durable project records in `Writes:` metadata whenever the workflow expects implementation to update those records. A continuation checkpoint, feedback record, or similar file outside the active feature directory is not Spec Kit bookkeeping merely because it supports the development workflow.

After task refinement, the Spec Kit integration should inspect the deterministic ordered union of declared writes through Boundary's target-context query. Unowned or ambiguously owned ordinary targets should therefore be reported before implementation entry rather than discovered only from an actual write at verification. This inspection remains non-authorizing and is not saved as operation evidence.

Implementation authorization requires an explicit task-ID selection. The adapter gate accepts repeated `--task` arguments for direct invocation. The workflow overlay transports the same operation input through the transient `BOUNDARY_TASK_IDS` environment value as a JSON array.

`BOUNDARY_TASK_IDS` is integration transport only. It is not persistent project state or operation evidence.

The adapter projects only the selected tasks' writes into the requested implementation unit. No task selection means no implementation authorization; it does not mean the entire feature.

The adapter gate also exposes a non-blocking `status` query containing Boundary's compact authorization handoff plus whether its change identity matches the active Spec Kit feature. The query does not select tasks, authorize writes, or verify the operation.

The adapter is installed with Spec Kit extension identity `boundary`. Under Spec Kit's canonical extension-command namespace, this yields the two public wrappers:

- `speckit.boundary.authorize` at implementation entry;
- `speckit.boundary.verify` at implementation exit.

Those wrappers invoke native Boundary authorization and verification. They are adapter commands, not alternate product identities.

The workflow overlay owns the two blocking lifecycle transitions. It requires explicit selection input before its authorization gate and never reconstructs feature-wide scope.

Spec Kit planning and task refinement use `boundary inspect` on demand, including declared-scope readiness checks. There is no public persisted context phase and no public validation phase.

The extension does not duplicate workflow-overlay authorization and verification as hooks.

Spec Kit feature artifacts and `.specify/` state are adapter-owned for actual-write classification unless a path is itself an authorized implementation target or a native Boundary contract. That classification cannot hide an authorized or contract path because Boundary checks those classes before consulting the adapter classifier.

## Core isolation

Boundary core must not contain assumptions about:

- host feature directory names;
- host task document names or syntax;
- workflow stage names;
- host command namespaces;
- constitutions or equivalent host policy documents;
- extension, preset, hook, or overlay concepts;
- generated agent discovery paths.

Those concerns belong to concrete adapters.

A replacement change system should therefore require a new adapter implementation, not changes to native contracts, authorization, agent procedure, or verification semantics.

## Determinism

Given the same host change state and the same explicit task selection, the adapter must produce the same normalized implementation unit.

Adapter projection must not depend on transient agent conversation state.

Authorization and verification consume fresh host state at their respective lifecycle transitions rather than trusting a stale planning projection.

Verification remains bound to historical operation evidence even if the host task projection changes after authorization.

Declared-scope preflight is likewise recomputed from current structured host state when requested. Its output is advisory and never substitutes for fresh authorization-time resolution.

## Failure behavior

Malformed or ambiguous structured change state is a blocking adapter error.

Missing change identity, missing implementation-unit selection, unknown or duplicate selected task identity, duplicate task identity in the change, repeated write ownership between tasks, invalid write paths, empty selected-unit writes, or invalid adapter-owned path declarations must not be converted into permissive defaults.

When the adapter cannot represent required implementation scope, implementation remains unauthorized until the host state or explicit unit selection is corrected.

Planning/readiness diagnostics may additionally identify unowned or ambiguously owned writes elsewhere in the declared change before their task is selected. Those diagnostics do not enlarge the selected unit or become historical authorization evidence.
