# Agent Instruction Architecture

Boundary uses progressive disclosure so agent context contains stable procedure plus only the project facts relevant to current work.

The architecture does not replace a legacy framework bootstrap with another large always-loaded instruction file.

## Instruction classes

Boundary separates four kinds of information.

### Stable Boundary policy

A small set of product invariants may always be available:

- persistent contracts are canonical system constraints;
- applicable contracts are additive;
- implementation may not write undeclared targets;
- contract evolution is separate from dependent implementation;
- deterministic authorization and verification are authoritative.

Stable policy contains no project-specific contracts or current operation state.

### Procedural skills

Reusable agent procedure lives in canonical Boundary skills.

Skills contain no current feature IDs, target paths, hashes, owners, tool versions, or generated operation state.

### Operation facts

Current facts are derived on demand:

- declared writes;
- target owner and applicable contracts;
- relevant invariants, prohibitions, and dependency interfaces;
- authorization status;
- selected implementation task identities and authorized targets;
- current-versus-baseline Git freshness;
- verification findings.

These facts belong in deterministic tool output rather than stable skill text.

### Deterministic enforcement

Code enforces scope, ownership, Git state, and operation-kind rules.

Skills explain agent behavior around those mechanisms but are not the authorization or correctness boundary.

## Canonical skills

Boundary v1 defines three procedural capabilities.

### `boundary-scope`

Use while planning implementation or refining tasks.

It identifies exact intended writes, separates implementation from contract evolution, inspects effective context, records structured write declarations, and keeps exploratory path mentions out of authorization scope.

It may prefer owner-local task decomposition where useful while keeping legitimate coordinated multi-owner work representable.

It does not authorize implementation.

### `boundary-implement`

Use only after successful implementation authorization.

It establishes current authority from deterministic `boundary status` output, inspects effective context before changing targets, preserves all applicable constraints, writes only authorized targets, stops before scope expansion, and transitions to contract evolution when required behavior cannot satisfy current contracts.

It does not alter authorization evidence.

### `boundary-contracts`

Use for deliberate persistent-contract evolution.

It identifies the smallest durable contract change, preserves additive scope semantics, modifies only contract files, runs structural contract validation, and requires fresh dependent implementation authorization afterward.

It is not part of ordinary implementation unless the lifecycle explicitly transitions to contract evolution.

## Skill source and materialization

Canonical skill procedure is stored as plain Markdown in:

    skills/scope/SKILL.md
    skills/implement/SKILL.md
    skills/contracts/SKILL.md

Canonical files contain Boundary procedure only. They contain no runtime discovery frontmatter or runtime-specific paths.

The concrete Codex adapter materializes the named skills under `.agents/skills/`. The concrete Claude Code adapter materializes the same named skills under `.claude/skills/`.

Each materialized file consists only of fixed runtime discovery metadata followed by canonical skill bytes.

Materialization is deterministic and idempotent. Feature, task, authorization, and operation state cannot alter generated skill bytes.

Generated materializations are not canonical source.

Codex and Claude Code remain concrete adapters rather than members of a generalized runtime-provider framework.

## Effective-context query

Boundary provides an on-demand query equivalent to:

    boundary inspect <target>

The agent-oriented result includes only relevant facts, including target path, primary owner, applicable contracts, semantic items with provenance, relevant dependency interfaces, and canonical source identities.

Agents may request raw canonical contracts when a projection is insufficient.

Planning and task refinement query this context on demand. They do not create a persisted planning-context lifecycle state.

For the Spec Kit adapter, only exact structured `Writes:` declarations become authorization input.

## Installed semantic command surface

Installed downstream projects use the mise-installed `boundary` executable for semantic operations:

    boundary inspect <target...>
    boundary authorize --task <task-id>
    boundary verify
    boundary status
    boundary contracts check

Agents do not reconstruct Python import paths, package locations, adapter script paths, copied-runtime locations, or uv cache configuration during ordinary downstream work.

`boundary status` emits the compact `boundary.authorization-handoff/v1` document.

When an operation exists, the handoff projects:

- operation and change identity;
- operation kind and status;
- selected task identities;
- exact authorized target evidence;
- contract-graph identity;
- authorization-time Git HEAD;
- current Git HEAD;
- whether the two HEAD values match.

The handoff is query output derived from historical operation evidence and current repository state. It does not reconstruct authority from mutable change-system planning files and does not become another persistent source of truth.

A delegated implementation worker requires an implementation operation with `status: authorized`, an authorized target, and a matching Git baseline before writing.

The installed `boundary` command delegates `authorize` and `verify` to the packaged change-system adapter while keeping adapter module layout out of normal agent procedure.

## Bootstrap independence

Boundary installation and normal operation do not require a project-wide provider bootstrap as an instruction source.

Historical repositories may contain legacy bootstrap files, but Boundary does not copy their instructions into a global prompt or consult them for native authorization.

## Context loading limits

Normal implementation does not automatically load every project contract, all dependency contracts recursively, legacy bootstrap text, generated authorization records, or unrelated historical feature artifacts.

A contract is loaded because its scope or direct dependency relationship makes it relevant.

Boundary v1 does not maintain a global catch-all project contract in always-on context. Durable cross-component rules use explicit scoped relationship contracts.

## Context ordering

Where an agent runtime permits ordering, Boundary context should progress from stable to volatile:

1. generic agent/runtime instructions;
2. small stable Boundary policy;
3. invoked Boundary skill;
4. effective project contract context;
5. change/task state;
6. active authorization facts;
7. relevant source and tests;
8. immediate user request and latest findings.

Volatile identifiers and hashes must not be placed in stable skill files.

## Adapter portability

Canonical skills use product-level verbs such as inspect target context, declare write scope, authorize implementation, verify operation, and evolve contracts.

They do not require a specific agent function name or change-system command.

Concrete runtime differences remain in concrete adapters rather than leaking into canonical skill content.

The Spec Kit adapter exposes only implementation-entry and implementation-exit wrappers. The workflow overlay owns those blocking transitions.

## Failure behavior

When deterministic tooling reports an unresolved owner, undeclared target, invalid contract graph, stale operation, or other blocking state:

- the agent does not infer permission;
- the relevant skill directs the supported lifecycle transition;
- deterministic tooling remains authoritative.

Prompt wording never converts a deterministic failure into permission.

## Evaluation criteria

The instruction architecture is tested for small runtime-neutral canonical skills, deterministic materialization, stable skill bytes, compact worker handoff, explicit write-scope discipline, reliable scope expansion, correct contract-evolution transitions, additive constraint preservation, clear provenance, and low-context use of the installed semantic command surface.
