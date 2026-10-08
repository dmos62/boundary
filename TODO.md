# Boundary feedback resolution plan

Source: `../gui-auto2/BOUNDARY-FEEDBACK.md` (read-only).

The final 2026-10-08 feedback entry supersedes the earlier claim that operation `c47c942cc21e42cfb237e9663dd40564` remains open. That operation and its dependent evidence-record implementation operation both verified successfully.

Do not recover, reopen, reconstruct, or edit either operation record.

## Completed: Contract-evolution CLI development verification

The lifecycle-classification correction and installed development CLI workflow passed the supplied 2026-10-08 validation.

The correction:

- Passes the actual operation kind to lifecycle outcome classification.
- Preserves `implementation` as the default for existing adapter callers.
- Passes `contract-evolution` from the native verification CLI entrypoint.
- Prevents an ordinary write during contract evolution from being misclassified as requiring another contract-evolution transition.
- Preserves existing implementation-operation classification.
- Leaves native actual-write verification authoritative.

Recorded validation:

- Complete unittest suite: 147 tests, zero failures.
- Lifecycle outcome classification: 5 passed, including both regressions.
- Installed executable contract-evolution integration: 4 passed.
- Focused contract-evolution CLI regressions: 9 passed.
- Native contract ownership tests: 4 passed.
- Mise distribution tests: 2 passed.
- Installed CLI help and command surface: passed.
- Native contract validation: 15 contracts valid.
- Boundary integration health: passed.
- Generated `.specify/boundary-runtime` absence check: passed.
- Git whitespace checks: passed.
- Changed canonical code/documentation 250-line limit: passed.

The installed integration exercises authorization, native contract modification, contract checking, verification, persisted operation identity and kind, Spec Kit bookkeeping exclusions, and rejection of unauthorized ordinary, contract, and unrelated-feature writes.

Failed verification retains nonzero exit status, structured diagnostics, and an authorized operation. Successful verification preserves operation identity and persists native closure evidence. Contract evolution grants no implementation authority; fresh explicit task selection and implementation authorization remain necessary.

These are supplied repository command results, not independent release qualification. The executable reports `0.2.1.dev3+g4e44cf6fa.d20261007`, a development installation. Its version does not demonstrate a released fix.

## 1. Resolve downstream Feature 005 CLI interface ownership

Status: ownership design established from supplied downstream inspection; mutation remains blocked until execution in the downstream repository with successful Boundary authorization.

### Confirmed downstream facts

The supplied 2026-10-08 read-only commands establish:

- Downstream repository: `../gui-auto2`.
- Branch: `005-dev-chrome-session`.
- Git status contains an unrelated untracked `TEST_SECRET_DONT_READ` entry. Do not inspect or modify that entry.
- `specs/005-dev-chrome-session/contracts/cli.md` has no primary owner and no applicable contracts.
- `apps/chrome-dev-session/src/cli.rs` and `apps/chrome-dev-session/tests/cli.rs` have primary owner `chrome-dev-session`.
- Both Rust targets also receive applicable `desktop-host-windows` constraints.
- The native owner contract is `contracts/chrome-dev-session.contract.md`.
- Its current `owns` array contains `apps/chrome-dev-session/**`.
- Its `depends_on` array contains `desktop-host-windows`.
- The contract's purpose and interfaces explicitly describe the development Chrome session launcher.
- The supplied native graph declarations do not show another owner of the exact Feature 005 CLI interface path.
- The downstream operation `79dab3e79f264bb39f95fb8036ed97ef` is verified, not authorized for new writes.
- The operation's Git baseline differs from current HEAD; this does not reopen the verified operation.
- The Boundary 0.3.0 downstream installation previously exhibited the contract-evolution verification dispatch defect.

The supplied downstream task inspection also establishes:

- T001 declares `apps/chrome-dev-session/tests/cli.rs`.
- T002 declares `apps/chrome-dev-session/src/cli.rs`.
- T004 declares `tests/desktop/dev-chrome-session.md`.
- T005 refers to the interface contract in descriptive prose but has no structured `Writes:` declaration.
- No displayed structured task declaration contains `specs/005-dev-chrome-session/contracts/cli.md`.
- The interface must be added to the appropriate existing task's exact structured write scope before implementation authorization.
- The same path must not be declared by two separate tasks.

The previous TODO's downstream-access blocker has therefore been narrowed: the supplied repository environment could inspect the downstream tree, but the current execution environment does not expose that working tree or its installed Boundary executable. Supplied command results are read-only evidence, not live authorization.

No downstream contract, interface specification, implementation target, operation record, or feedback file was changed in this iteration.

### Ownership decision

Use the existing `chrome-dev-session` contract rather than introducing a dedicated interface contract.

Its architectural purpose already covers the CLI interface. The existing dependency and launcher constraints are applicable, and the inspected native graph does not identify a competing owner.

Add exactly one ownership declaration to the existing `owns` array:

    - specs/005-dev-chrome-session/contracts/cli.md

Retain:

    - apps/chrome-dev-session/**

Preserve the existing dependency, purpose, invariants, prohibitions, and interfaces unchanged.

This exact-path ownership gives the interface one primary owner without extending ownership to unrelated specification files, Feature 005 directories, or other change-system artifacts.

An additional `applies_to` declaration is not needed for the identified repair. It cannot substitute for primary ownership.

If a fresh downstream inspection reveals graph changes, re-evaluate this decision before authorization rather than forcing an incompatible declaration.

### Required downstream contract-evolution transition

Execute from `../gui-auto2` using an installed Boundary executable with working public contract-evolution closure.

1. Review `AGENTS.md`, `docs/spec.md`, and relevant focused downstream specifications.
2. Confirm branch, Git status, the complete native contract graph, and the current operation handoff.
3. Inspect the exact interface and Rust targets through Boundary.
4. Confirm the active operation remains verified.
5. Confirm the installed CLI supports contract-evolution verification. Do not rely solely on command help or a development-installation result.
6. Select a stable change identity associated with the ownership repair.
7. Authorize exactly `contracts/chrome-dev-session.contract.md`:

       mise exec -- boundary contracts authorize --change CHANGE_ID contracts/chrome-dev-session.contract.md

8. Require `status: authorized` and confirm the exact authorized target.
9. Add only the exact interface ownership declaration specified above.
10. Validate the native graph:

       mise exec -- boundary contracts check

11. Reinspect the interface and implementation targets:

       mise exec -- boundary inspect specs/005-dev-chrome-session/contracts/cli.md apps/chrome-dev-session/src/cli.rs apps/chrome-dev-session/tests/cli.rs

12. Require `chrome-dev-session` as the interface's single primary owner. Confirm existing Rust ownership and additive constraints remain intact.
13. Verify and close the contract-evolution operation:

       mise exec -- boundary verify

14. Require `status: verified`, unchanged operation identity, and no blocking diagnostics.
15. Confirm closure through the read-only operation handoff:

       mise exec -- boundary status

Do not proceed with the contract edit if authorization is blocked. Do not invoke undocumented internal verification APIs as a substitute for a defective released CLI.

Do not write the interface document during contract evolution.

### Required dependent task transition

After successful contract-evolution closure:

1. Inspect the complete Feature 005 structured task declarations and current feature state.
2. Determine the existing owning task for the follow-up CLI behavior and corresponding interface update.
3. Refine that task's exact `Writes:` declaration to include the CLI interface path.
4. Include all other implementation files genuinely required by that selected task.
5. Do not duplicate the interface path in a second task.
6. Treat changes to durable task records as ordinary writes unless the active change system genuinely classifies them as bookkeeping.
7. Run declared-scope preflight over the deterministic complete task write projection.
8. Require every declared implementation target to have exactly one primary owner.
9. Explicitly select the dependent implementation task or task unit.
10. Obtain fresh implementation authorization.
11. Run `boundary inspect --authorized` and check the exact authorized targets and effective context.
12. Only then make authorized dependent implementation writes.
13. Verify the implementation separately after ordinary project checks.

T004 remains an acceptance/evidence task. Do not mark it complete based solely on Boundary authorization or verification.

### Acceptance criteria

- The interface path resolves to exactly one primary owner, `chrome-dev-session`.
- Existing launcher ownership and additive architectural constraints remain effective.
- The downstream native contract graph passes validation.
- Contract evolution verifies through the actual installed public CLI.
- The evolution operation retains its identity through closure.
- The dependent task declares the exact interface path in structured `Writes:` metadata.
- No duplicate structured declaration owns the interface write.
- Declared-scope preflight succeeds across the intended implementation unit.
- Dependent implementation has separate fresh authorization.
- No unrelated Feature 005 behavior, historical operation state, or private environment data is changed.
- `../gui-auto2/BOUNDARY-FEEDBACK.md` remains unchanged.

## 2. Confirm the released contract-evolution entrypoint

Status: development installation validated; qualifying released distribution remains unverified.

Boundary 0.3.0 introduced public contract-evolution authorization, but the downstream verification dispatch defect requires a released correction.

Supported workflow:

    boundary contracts authorize --change CHANGE_ID CONTRACT...
    boundary contracts check
    boundary verify

### Procedure

1. Establish which released Boundary distribution, if any, contains the completed dispatch and lifecycle-classification corrections.
2. Inspect the actual released Git source identity rather than inferring correctness from a tag name or development version.
3. Confirm authorization and closure using the released installed executable, not the editable development source installation.
4. Check command help, required arguments, nonzero blocking exit statuses, and structured lifecycle diagnostics.
5. Confirm implementation and contract-evolution operations dispatch to the correct verification paths.
6. Confirm the Spec Kit path classifier excludes only valid change-system bookkeeping and never masks authorized or native contract writes.
7. Confirm mise installation exposes the same semantic commands and canonical skill guidance.
8. Review installed end-to-end regression coverage.
9. Document the minimum released Boundary version containing the complete workflow.
10. Do not introduce a redundant second contract-evolution verification command.
11. Mark the original 0.2.0 missing-entrypoint defect superseded only after demonstrating the released installed workflow.

If no qualifying release exists, retain this task and proceed through the documented distribution process before using the correction for downstream contract evolution.

## 3. Release and downstream validation

Perform after the corresponding changes pass verification.

1. Run relevant unit, CLI, integration, and regression tests.
2. Run installed integration health and repository hygiene checks.
3. Enforce the 250-line limit for changed canonical code and documentation.
4. Confirm generated integration files do not replace canonical procedure or implementation.
5. Review `docs/spec-distribution.md` before preparing a release through the documented mise-managed distribution procedure.
6. Validate the released executable in a clean downstream installation.
7. Confirm contract-evolution closure with active Spec Kit bookkeeping.
8. Confirm Feature 005 interface ownership can be established without widening implementation authority.
9. Require fresh dependent implementation authorization.
10. Record resolved items and outstanding downstream migration instructions before clearing this TODO.

### Distribution caution

The reported development executable version is not release qualification.

The downstream 0.3.0 failure must not be considered fixed merely because prepared source or a development installation passes tests.

Investigate the observed mise source-tag and immutable-source-identity behavior against `docs/spec-distribution.md`.

The supplied downstream 0.3.0 lock evidence names a tag without demonstrating an immutable commit identity. The source checkout and peeled tag matched when checked, but that alone does not prove the distribution contract's lock guarantee.

Do not introduce another Boundary-owned revision-lock format.

## Scope and exclusions

- Do not edit `../gui-auto2/BOUNDARY-FEEDBACK.md`.
- Do not inspect or modify the downstream untracked `TEST_SECRET_DONT_READ` entry.
- Do not reopen or reconstruct already verified operation records.
- Do not modify persistent contracts during an implementation operation.
- Do not use contract evolution to authorize ordinary implementation writes.
- Do not alter Feature 005 calibration or launcher behavior while fixing Boundary.
- Do not equate Boundary verification with downstream application acceptance.
- Do not treat generated `.agents/` or `.specify/` material as canonical source.
- Do not treat historical migration material as current Boundary behavior.
- Do not treat passing development-installation tests as proof of release readiness.
- Do not perform downstream writes using authorization inferred from supplied command output.

The next priority remains the downstream Feature 005 ownership repair, executed under actual Boundary authorization. The subsequent priority is qualification of a released Boundary distribution and downstream validation.
