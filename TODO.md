# Boundary feedback resolution plan

Source: `../gui-auto2/BOUNDARY-FEEDBACK.md` (read-only).

The final 2026-10-08 feedback entry supersedes the earlier claim that operation `c47c942cc21e42cfb237e9663dd40564` remains open. That operation and its dependent evidence-record implementation operation both verified successfully.

Do not recover, reopen, reconstruct, or edit either operation record.

## Completed: Contract-evolution CLI verification

The prepared lifecycle-classification correction and installed contract-evolution CLI workflow passed the supplied 2026-10-08 validation.

The correction:

- Passes the actual operation kind to lifecycle outcome classification.
- Preserves `implementation` as the default for existing adapter callers.
- Passes `contract-evolution` from the native verification CLI entrypoint.
- Prevents an ordinary write during contract evolution from being misclassified as requiring another contract-evolution transition.
- Preserves the existing implementation-operation classification.
- Leaves native actual-write verification authoritative.

Recorded validation:

- Complete unittest suite: 147 tests, zero failures.
- Lifecycle outcome classification: 5 passed, including both new regressions.
- Installed executable contract-evolution integration: 4 passed.
- Focused contract-evolution CLI regressions: 9 passed.
- Installed CLI help and command surface: passed.
- Native contract validation: 15 contracts valid.
- Boundary integration health: passed.
- Generated `.specify/boundary-runtime` absence check: passed.
- Git whitespace checks: passed.
- Changed canonical code/documentation 250-line limit: passed.

The installed integration exercises authorization, native contract modification, contract checking, verification, persisted operation identity and kind, Spec Kit bookkeeping exclusions, and rejection of unauthorized ordinary, contract, and unrelated-feature writes.

Failed verification retains nonzero exit status, structured diagnostics, and an authorized operation. Successful verification preserves operation identity and persists native closure evidence. Contract evolution grants no implementation authority; fresh explicit task selection and implementation authorization remain necessary.

These are supplied repository command results, not independent release qualification. The executable reports `0.2.1.dev3+g4e44cf6fa.d20261007`, a development installation. Its version does not demonstrate a released fix.

## 1. Establish supported ownership for the Spec Kit interface contract

Status: unresolved for `specs/005-dev-chrome-session/contracts/cli.md` in the downstream `../gui-auto2` project.

Rust source and test targets resolve to owner `chrome-dev-session`. The CLI interface contract has no primary owner.

Native Boundary contracts support exact-path ownership. No catch-all owner, implicit feature ownership, or runtime exception is required.

### Procedure

1. Inspect the downstream native contract graph and effective Boundary context for:
   - `specs/005-dev-chrome-session/contracts/cli.md`
   - `apps/chrome-dev-session/src/cli.rs`
   - `apps/chrome-dev-session/tests/cli.rs`
2. Inspect existing architectural ownership and additive applicability before selecting the smallest durable contract change.
3. Select an appropriate existing architectural owner or introduce a narrowly scoped interface owner.
4. Ensure any current operation is verified before contract evolution; do not reopen historical operations.
5. Authorize evolution of the exact affected native contract files using `boundary contracts authorize --change CHANGE_ID CONTRACT...`.
6. Establish exactly one primary owner for the interface target while preserving all applicable constraints.
7. Run `boundary contracts check` and `boundary verify`; require a verified contract-evolution operation.
8. Require the exact interface-contract path in the appropriate structured task `Writes:` declaration.
9. Run declared-scope preflight across source, test, and interface-contract targets.
10. Require fresh explicit implementation task selection and authorization before dependent implementation writes.

### Acceptance

- The exact interface path has one unambiguous primary owner.
- Additive constraints remain effective.
- The affected task declares every required implementation write.
- Native contract evolution verifies successfully.
- Declared-scope preflight resolves every target.
- Dependent implementation receives separate, fresh authorization.

Leave `../gui-auto2/BOUNDARY-FEEDBACK.md` and Feature 005 implementation unchanged during Boundary repair.

Do not modify downstream files without the required Boundary authorization. If downstream access or authorization is unavailable, record the precise blocker and migration instructions rather than bypassing the lifecycle.

## 2. Confirm the released contract-evolution entrypoint

Status: development installation validated; released distribution remains unverified.

Boundary 0.3.0 introduced public contract-evolution authorization, but its verification dispatch defect requires a released correction.

Supported workflow:

    boundary contracts authorize --change CHANGE_ID CONTRACT...
    boundary contracts check
    boundary verify

### Procedure

1. Establish which released Boundary distribution, if any, contains the completed dispatch and classification corrections.
2. Confirm authorization and closure using its actual installed executable, not the development source installation.
3. Check command help, argument validation, nonzero blocking exit statuses, and structured lifecycle diagnostics.
4. Confirm both operation kinds are dispatched correctly.
5. Confirm mise installation exposes the same semantic commands and canonical skill guidance.
6. Review installed end-to-end regression coverage.
7. Document the minimum released Boundary version containing the complete workflow.
8. Do not introduce a redundant second contract-evolution command.
9. Mark the original 0.2.0 missing-entrypoint defect superseded only after demonstrating the released installed workflow.

If no qualifying release exists, retain this task and proceed through the documented distribution process.

## 3. Release and downstream validation

Perform after the corresponding changes pass verification.

1. Run relevant unit, CLI, integration, and regression tests.
2. Run installed integration health and repository hygiene checks.
3. Enforce the 250-line limit for changed canonical code and documentation.
4. Confirm generated integration files do not replace canonical procedure or implementation.
5. Review `docs/spec-distribution.md` before preparing a release through the documented mise-managed distribution procedure.
6. Validate the released executable in a clean downstream installation.
7. Confirm contract-evolution closure with active Spec Kit bookkeeping.
8. Confirm Feature 005 interface-contract ownership can be established without widening implementation authority.
9. Require fresh dependent implementation authorization.
10. Record resolved items and outstanding downstream migration instructions before clearing this TODO.

### Distribution caution

The reported development executable version is not a release qualification. The downstream 0.3.0 failure must not be considered fixed merely because the prepared source or development installation passes tests.

Investigate the mise source-tag and immutable-source-identity observation against `docs/spec-distribution.md`. Do not introduce another Boundary-owned revision-lock format.

## Scope and exclusions

- Do not edit `../gui-auto2/BOUNDARY-FEEDBACK.md`.
- Do not reopen or reconstruct already verified operation records.
- Do not modify persistent contracts during an implementation operation.
- Do not use contract evolution to authorize ordinary implementation writes.
- Do not alter Feature 005 calibration or launcher behavior while fixing Boundary.
- Do not equate Boundary verification with downstream application acceptance.
- Do not treat generated `.agents/` or `.specify/` material as canonical source.
- Do not treat historical migration material as current Boundary behavior.
- Do not treat passing tests in a development installation as proof of release readiness.

The next priority is resolving the Feature 005 CLI interface-contract ownership defect through supported contract evolution, followed by released distribution and downstream verification.
