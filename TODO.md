# Boundary feedback resolution plan

Source: `../gui-auto2/BOUNDARY-FEEDBACK.md` (read-only).

The final 2026-10-08 feedback entry supersedes the earlier claim that operation `c47c942cc21e42cfb237e9663dd40564` remains open. That operation and the dependent evidence-record implementation operation both verified successfully.

Do not recover, reopen, reconstruct, or edit either operation record.

## 1. Complete contract-evolution CLI verification

Status: implementation prepared; focused regressions passed; complete validation and installed end-to-end validation remain outstanding.

### Prepared implementation

- Public `boundary verify` dispatches by historical operation kind.
- Implementation operations retain the existing Spec Kit adapter verification path.
- Contract-evolution operations use native `finalize_operation_verification`.
- Spec Kit bookkeeping classification derives deterministically from the historical operation change identity.
- Native verification remains the sole authority for actual-write verification.
- Unauthorized contract writes and ordinary implementation writes remain prohibited during contract evolution.
- CLI help and canonical contract-evolution skill describe the same closure workflow.
- Regression tests cover successful closure, feature bookkeeping exclusion, operation-kind violations, unauthorized writes, diagnostic stability, and CLI help.

The implementation currently involves:

- `src/boundary/cli/main.py`
- `src/boundary/cli/contract_verification.py`
- `tests/test_contract_evolution_verification_cli.py`
- `skills/contracts/SKILL.md`

Preserve the prepared changes unless validation reveals a specific defect.

### Validation evidence from 2026-10-08

Passed:

- Focused contract-evolution CLI tests: 9.
- Native verification tests: 7.
- Authorization lifecycle tests: 8.
- Distribution surface tests: 4.
- Lifecycle outcome tests: 3.
- Operation persistence tests: 7.
- Installed CLI command-help invocations.
- `mise exec -- boundary contracts check`: 15 contracts valid.
- `mise exec -- boundary integration check`.
- Absence check for `.specify/boundary-runtime`.
- `git diff --check` and `git diff --cached --check`.
- Changed canonical code and documentation line-count check, including untracked files.

The shortened `src/boundary/cli/main.py` passed the line-count check at 247 lines. Other changed canonical Python and Markdown files were below 250 lines.

The complete unittest suite ran 141 tests and failed one:

- `test_agent_skills.CanonicalBoundarySkillTests.test_contract_skill_enforces_operation_separation`
- Expected literal marker: `Modify only native contract files`
- The updated skill had equivalent semantics but did not contain that exact marker.

The skill wording has been adjusted to restore the required marker while retaining exact authorization semantics. The full suite has not been rerun after that adjustment.

These results do not establish release readiness.

### Remaining verification

1. Rerun `test_agent_skills.py` and the focused contract-evolution CLI regressions after the skill correction.
2. Review the installed `boundary_host.adapter.path_classifier` and `boundary_host.outcomes.outcome_for_error` against the new CLI entrypoint.
3. Review the native verification service signature, operation identity checks, result fields, blocked categories, diagnostic codes, and nonzero exit behavior.
4. Run the complete unittest suite and require zero failures.
5. Run `mise exec -- boundary integration check` and native contract validation.
6. Run repository whitespace and changed-file line-count checks, including untracked files.
7. Require every changed canonical code or documentation file to contain at most 250 lines.
8. Confirm generated `.agents/` and `.specify/` material is not used as canonical source.
9. Exercise the actual installed CLI in an isolated Git repository with active Spec Kit plan and task bookkeeping:
   - `boundary contracts authorize --change CHANGE_ID CONTRACT...`
   - Modify only the authorized native contract.
   - `boundary contracts check`
   - `boundary verify`
10. Confirm the final CLI result has `status: verified` and the persisted operation has kind `contract-evolution` and status `verified`.
11. Confirm authorized contract changes are accepted, Spec Kit bookkeeping is excluded, and unauthorized ordinary writes remain blocked.
12. Confirm the next dependent implementation requires a fresh explicit task selection and implementation authorization.

Do not classify task 1 as resolved until full validation and the installed CLI workflow succeed.

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
8. Require fresh implementation authorization before any dependent implementation writes.

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
4. Add installed end-to-end regression coverage if a coverage gap remains.
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

The next priority is task 1 validation, beginning with the corrected skill regression and the complete test suite. Tasks 2 and 3 can proceed separately after the public CLI closure path is established.
