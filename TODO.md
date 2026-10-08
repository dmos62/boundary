# Boundary feedback resolution plan

Source: `../gui-auto2/BOUNDARY-FEEDBACK.md` (read-only).

The final 2026-10-08 feedback entry supersedes the earlier claim that operation `c47c942cc21e42cfb237e9663dd40564` remains open. That operation and the dependent evidence-record implementation operation both verified successfully. Do not recover, reopen, reconstruct, or edit either operation record.

## 1. Complete contract-evolution CLI verification

Status: focused regression validation passed; full-suite and installed end-to-end validation remain outstanding.

The prepared implementation:

- Dispatches public `boundary verify` by historical operation kind.
- Retains the existing Spec Kit adapter verification path for implementation operations.
- Uses native `finalize_operation_verification` for contract-evolution closure.
- Derives deterministic Spec Kit bookkeeping classification from the historical operation change identity.
- Preserves native verification policy without introducing another write verifier.
- Rejects unauthorized contract writes and ordinary implementation writes during contract evolution.
- Includes regression coverage for closure, feature bookkeeping exclusion, operation-kind violations, unauthorized writes, diagnostic stability, and CLI help.
- Documents the intended public contract-evolution workflow in the canonical skill and CLI help.

Validation reported by the current iteration:

- Focused contract-evolution CLI tests: 9 passed.
- Native verification tests: 7 passed.
- Authorization lifecycle tests: 8 passed.
- Distribution surface tests: 4 passed.
- Lifecycle outcome tests: 3 passed.
- `mise exec -- boundary integration check`: passed.
- Generated `.specify/boundary-runtime` absence check: passed.
- `git diff --check`: passed.
- Changed-file line-count check: failed because `src/boundary/cli/main.py` had 254 lines.

The CLI file has now been shortened to address that limit. The revised working tree has not yet been revalidated.

Remaining work:

1. Review the installed `boundary_host.adapter.path_classifier`, `boundary_host.outcomes.outcome_for_error`, and native verification service signatures against the new CLI path.
2. Confirm lifecycle result fields, blocked categories, diagnostic codes, and nonzero exit behavior against the installed adapter.
3. Rerun focused regressions after the CLI line-count correction.
4. Run the complete relevant test suite.
5. Run `mise exec -- boundary integration check`.
6. Run `git diff --check` and the changed-file line-count check, including new untracked Python and Markdown files.
7. Confirm every changed canonical code or documentation file contains at most 250 lines.
8. Confirm no generated `.agents/` or `.specify/` content is used as canonical source.
9. Exercise an actual installed `boundary contracts authorize` → `boundary contracts check` → `boundary verify` workflow in an isolated Git repository with active Spec Kit plan and task bookkeeping.
10. Confirm the operation is persistently verified and dependent implementation requires fresh authorization.

Do not classify this task as resolved until full validation and the installed CLI workflow succeed.

## 2. Establish supported ownership for Spec Kit interface contracts

Status: unresolved for `specs/005-dev-chrome-session/contracts/cli.md` in the downstream project.

The Rust implementation and test targets have owner `chrome-dev-session`. The CLI interface contract lacks a primary owner.

Native Boundary contract semantics already support exact-path ownership. No catch-all owner, implicit feature ownership, or runtime exception is necessary.

Next steps:

1. Inspect the downstream native contract graph and effective context for the CLI contract, Rust implementation, and Rust test paths.
2. Select the existing appropriate architectural owner or a new narrow interface owner.
3. Evolve native `contracts/**/*.contract.md` declarations through an authorized contract-evolution operation.
4. Confirm exactly one primary owner and preserved additive applicability.
5. Require the exact interface-contract path in the appropriate structured task `Writes:` metadata.
6. Run declared-scope preflight across the source, test, and interface-contract targets.
7. Verify and close contract evolution before dependent implementation authorization.
8. Leave `../gui-auto2/BOUNDARY-FEEDBACK.md` and Feature 005 implementation unchanged during Boundary repair.

Acceptance requires exact ownership, additive constraints, declared writes, and fresh implementation authorization.

## 3. Confirm installed contract-evolution entrypoint

Status: the Boundary 0.2.0 missing-authorization-entrypoint limitation was partially superseded by Boundary 0.3.0. The public verification defect still requires installed end-to-end validation.

The intended workflow is:

    boundary contracts authorize --change CHANGE_ID CONTRACT...
    boundary contracts check
    boundary verify

After task 1:

1. Confirm authorization and closure through the installed CLI.
2. Check command help, argument validation, and blocked lifecycle diagnostics.
3. Confirm mise installation exposes the same commands and canonical skill guidance.
4. Add end-to-end authorization coverage if remaining gaps are found.
5. Document the minimum released Boundary version containing the complete workflow.
6. Do not introduce a redundant second contract-evolution command.
7. Mark the original 0.2.0 entrypoint defect superseded only after the installed workflow is demonstrated.

## 4. Release and downstream validation

Perform after the corresponding changes pass verification.

1. Run relevant unit, CLI, integration, and regression tests.
2. Run `mise exec -- boundary integration check` and repository hygiene checks.
3. Enforce the 250-line limit for changed canonical code and documentation.
4. Confirm canonical procedure and implementation are not replaced by generated `.agents/` or `.specify/` material.
5. Review `docs/spec-distribution.md` before preparing a versioned release through the documented mise-managed distribution procedure.
6. Validate the released executable in a clean downstream installation.
7. Confirm contract-evolution CLI closure works with active Spec Kit bookkeeping.
8. Confirm Feature 005 interface-contract ownership can be established without widening implementation authority.
9. Require fresh implementation authorization after contract evolution.
10. Record resolved items and remaining downstream migration instructions before clearing this TODO.

## Scope and exclusions

- Do not edit `../gui-auto2/BOUNDARY-FEEDBACK.md`.
- Do not reopen or reconstruct already verified operation records.
- Do not introduce another Boundary-owned lock format for the mise source-tag observation; assess reproducibility against `docs/spec-distribution.md`.
- Do not alter Feature 005 calibration or launcher behavior while fixing Boundary.
- Do not equate Boundary verification with downstream application acceptance.
- Do not modify persistent contracts during an implementation operation.
- Do not treat prepared changes or passing focused tests as proof of release readiness.

The next step remains completion of task 1 validation. Tasks 2 and 3 can proceed separately after the public CLI closure path is established.
