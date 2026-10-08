# Boundary feedback resolution plan

Source: `../gui-auto2/BOUNDARY-FEEDBACK.md` (read-only).

The final 2026-10-08 feedback entry supersedes the earlier claim that operation `c47c942cc21e42cfb237e9663dd40564` remains open. That operation and the dependent evidence-record implementation operation both verified successfully.

Do not recover, reopen, reconstruct, or edit either operation record.

## 1. Complete contract-evolution CLI verification

Status: prepared implementation and reported complete unittest suite pass; installed end-to-end verification remains to be confirmed.

### Prepared implementation

- `src/boundary/cli/main.py` dispatches `boundary verify` by historical operation kind.
- `src/boundary/cli/contract_verification.py` closes contract evolution through native `finalize_operation_verification`.
- Implementation verification continues through the Spec Kit adapter.
- Contract evolution supplies deterministic Spec Kit bookkeeping classification.
- Native verification remains authoritative for actual writes.
- `skills/contracts/SKILL.md` describes authorization, structural validation, closure, and fresh dependent authorization.
- `tests/test_contract_evolution_verification_cli.py` covers public CLI closure and failure diagnostics.
- `tests/test_installed_contract_evolution_workflow.py` adds subprocess-level installed executable coverage.

Preserve the prepared implementation unless validation identifies a specific defect.

### Recorded validation results from 2026-10-08

The supplied repository command results report:

- Complete unittest suite: 141 tests, zero failures.
- Focused contract-evolution CLI tests: 9 passed.
- Native verification tests: 7 passed.
- Authorization lifecycle tests: 8 passed.
- Distribution surface tests: 4 passed.
- Lifecycle outcome tests: 3 passed.
- Operation persistence tests: 7 passed.
- Installed CLI help invocations succeeded.
- Native contract validation: 15 contracts valid.
- Boundary integration health: passed.
- Generated `.specify/boundary-runtime` absence check: passed.
- Git whitespace checks: passed.
- Changed canonical file line-count check: passed.

The complete 141-test result supersedes the earlier failing skill regression. The canonical contracts skill now contains both required literal markers.

These results do not establish release readiness.

The installed executable reported version `0.2.1.dev3+g4e44cf6fa.d20261007`. This is a development installation, not evidence of a released version containing the fix.

### Remaining verification

1. Run the newly added installed executable integration tests:

       mise exec -- python -m unittest discover -s tests -p 'test_installed_contract_evolution_workflow.py' -v

2. Require successful closure through an actual `boundary` subprocess in an isolated Git repository containing active Spec Kit plan and task bookkeeping.

3. Confirm that the test exercises:

   - `boundary contracts authorize --change CHANGE_ID CONTRACT...`
   - Modification of only the authorized native contract.
   - `boundary contracts check`.
   - `boundary verify`.
   - Final CLI `status: verified`.
   - Persisted operation kind `contract-evolution` and status `verified`.
   - Exclusion of the current change's Spec Kit bookkeeping.
   - Blocking of unauthorized contracts, ordinary implementation writes, and other features' writes.

4. Review `boundary_host.adapter.path_classifier` and `boundary_host.outcomes.outcome_for_error` against the native closure entrypoint.

5. Review native verification operation identity, result fields, diagnostic codes, blocked categories, and nonzero exit behavior.

6. Rerun the complete unittest suite, now including the installed executable regressions, and require zero failures.

7. Rerun:

       mise exec -- boundary contracts check
       mise exec -- boundary integration check
       git diff --check
       git diff --cached --check

8. Check changed canonical code and documentation line counts, including untracked files, and require no file to exceed 250 lines.

9. Confirm generated `.agents/` and `.specify/` material is not used as canonical source.

10. Confirm fresh explicit task selection and implementation authorization are required for dependent implementation. Contract-evolution closure must not grant implementation write authority.

Do not classify this task as resolved until the installed executable workflow and full validation succeed.

## 2. Establish supported ownership for Spec Kit interface contracts

Status: unresolved for `specs/005-dev-chrome-session/contracts/cli.md` in the downstream project.

The Rust source and test targets resolve to owner `chrome-dev-session`. The CLI interface contract has no primary owner.

Native Boundary contracts support exact-path ownership. No catch-all owner, implicit feature ownership, or runtime exception is required.

After task 1:

1. Inspect the downstream native contract graph and effective context for the CLI interface contract, Rust source, and Rust test targets.
2. Select an appropriate existing architectural owner or introduce a narrow interface owner.
3. Authorize evolution of the exact affected native contract files.
4. Preserve additive applicability and establish exactly one primary owner for the interface target.
5. Run `boundary contracts check` and `boundary verify` to close evolution.
6. Require the exact interface-contract path in the appropriate structured task `Writes:` metadata.
7. Run declared-scope preflight across the source, test, and interface-contract targets.
8. Require fresh implementation authorization before dependent implementation writes.

Leave `../gui-auto2/BOUNDARY-FEEDBACK.md` and Feature 005 implementation unchanged during Boundary repair.

Acceptance requires exact ownership, additive constraints, declared writes, verified evolution, and fresh implementation authorization.

## 3. Confirm installed contract-evolution entrypoint

Status: Boundary 0.3.0 introduced public contract-evolution authorization, but its verification dispatch defect remains pending release validation.

The intended public workflow is:

    boundary contracts authorize --change CHANGE_ID CONTRACT...
    boundary contracts check
    boundary verify

After task 1:

1. Confirm authorization and closure through the installed CLI.
2. Check command help, argument validation, and blocked lifecycle diagnostics.
3. Confirm mise installation exposes the same commands and canonical skill guidance.
4. Review installed end-to-end regression coverage.
5. Document the minimum released Boundary version containing the complete workflow.
6. Do not introduce a redundant second contract-evolution command.
7. Mark the original 0.2.0 missing-entrypoint defect superseded only after the installed workflow is demonstrated.

## 4. Release and downstream validation

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

## Scope and exclusions

- Do not edit `../gui-auto2/BOUNDARY-FEEDBACK.md`.
- Do not reopen or reconstruct already verified operation records.
- Do not introduce another Boundary-owned lock format for the mise source-tag observation; assess reproducibility against `docs/spec-distribution.md`.
- Do not alter Feature 005 calibration or launcher behavior while fixing Boundary.
- Do not equate Boundary verification with downstream application acceptance.
- Do not modify persistent contracts during an implementation operation.
- Do not treat prepared changes or passing focused tests as proof of release readiness.

The next priority remains task 1: installed executable verification, complete regression rerun, and deterministic lifecycle review.
