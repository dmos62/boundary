# Boundary feedback resolution plan

Source: `../gui-auto2/BOUNDARY-FEEDBACK.md` (read-only).

The feedback contains three distinct problems. The final 2026-10-08 entry supersedes the earlier claim that the Feature 006 contract-evolution operation remains open. It does not resolve the CLI verification defect.

Work in the order below. Each implementation unit requires fresh Boundary authorization derived from selected structured task writes. Inspect effective target context before editing, and verify through the supported lifecycle. If additional writes become necessary, explicitly expand structured scope and obtain fresh authorization. Keep persistent-contract evolution separate.

## 1. Fix contract-evolution verification through the CLI

Priority: highest.

Status: unresolved in Boundary 0.3.0.

### Established facts

- `boundary contracts authorize` can create a native contract-evolution operation.
- The native verification service supports this operation kind.
- `boundary verify` currently routes through `boundary_host.adapter.verify_feature`, which rejects non-implementation operations with `OPERATION_CHANGED`.
- Contract-evolution verification must use the same Spec Kit path classifier as implementation verification, so active-feature bookkeeping is excluded correctly.
- Operation `c47c942cc21e42cfb237e9663dd40564` was successfully closed using the native verifier. No recovery or manual alteration of that operation is required.
- The subsequent evidence-record implementation operation also verified successfully.

### Planned resolution

1. Inspect `docs/spec-authorization.md`, `docs/spec-change-adapter.md`, and `docs/spec-lifecycle.md`, together with the current CLI dispatch, adapter, verification service, and tests.
2. Identify the narrowest shared verification path that supports both operation kinds without duplicating native verification policy.
3. Make the documented `boundary verify` entrypoint dispatch according to the active operation kind.
4. Preserve implementation-specific adapter behavior for implementation operations.
5. Route contract-evolution operations to native verification and finalization with the deterministic Spec Kit path classifier.
6. Preserve existing authorization evidence, baseline checks, actual-write checks, lifecycle diagnostics, and operation finalization semantics.
7. Ensure no verification path infers new authority or silently changes an operation's authorized targets.
8. Add regression tests for:
   - successful CLI verification and closure of an authorized contract-evolution operation;
   - active-feature plan/tasks bookkeeping excluded by the correct classifier;
   - unauthorized contract writes rejected;
   - contract-evolution operations not authorizing implementation writes;
   - existing implementation verification remaining functional;
   - failed verification leaving the operation unverified with stable diagnostics.
9. Align CLI help, contract-evolution skill guidance, and focused specifications with the actual supported closure command.
10. Run focused tests, integration health checks, and repository validation.

### Acceptance criteria

- The public CLI completes `authorize -> edit -> verify` for contract evolution without calling internal Python APIs.
- Contract-evolution verification uses the same relevant change-system classification as native implementation verification.
- Authorized contract-evolution operations close successfully; prohibited writes still block verification.
- Existing implementation verification behavior is preserved.
- Documentation and installed skill instructions describe a working supported workflow.

## 2. Establish supported ownership for Spec Kit interface contracts

Status: unresolved for `specs/005-dev-chrome-session/contracts/cli.md` in the reported downstream project.

### Established facts

- The affected Rust implementation and test paths have owner `chrome-dev-session`.
- The Feature 005 CLI interface contract has no primary owner or applicable contracts in the reported effective context.
- Explicit structured writes cannot be authorized for unowned targets.
- The downstream project requires the CLI contract to evolve alongside the launcher interface implementation.
- A broader implicit ownership or feature-wide authorization rule would contradict the native Boundary invariants.

### Planned resolution

1. Inspect `docs/spec-contracts.md`, `docs/spec-authorization.md`, and `docs/spec-change-adapter.md`.
2. Determine whether native contract semantics already allow a narrow owner to cover the exact Spec Kit interface-contract path.
3. Establish whether the downstream contract should be owned by an existing appropriate architectural owner or by a distinct, narrowly scoped interface owner.
4. Prefer existing native ownership and applicability declarations over new framework behavior.
5. Check for overlapping ownership, additive constraints, and primary-owner ambiguity before changing contracts.
6. If an ordinary native contract-evolution operation can establish this ownership, document the required downstream contract changes without editing the read-only feedback file.
7. If native semantics cannot represent the intended ownership, specify the missing behavior and authorize a separate Boundary implementation unit before modifying the runtime.
8. Confirm the downstream change system can explicitly declare the interface-contract write in the appropriate implementation task.
9. Inspect effective context and declared-scope preflight for the Rust sources, tests, and CLI contract after ownership is established.
10. Require fresh implementation authorization before the Feature 005 CLI change resumes.

### Acceptance criteria

- The CLI contract resolves to exactly one primary owner.
- All relevant additive constraints remain applicable.
- The contract path can participate in an explicitly selected task's write set.
- No authorization is derived from path-looking prose or unrelated tasks.
- Neither global catch-all ownership nor undocumented write exceptions are introduced.

## 3. Confirm and document the contract-evolution entrypoint

Status: reported missing in Boundary 0.2.0; partially addressed by Boundary 0.3.0.

### Established facts

- Boundary 0.2.0 exposed native contract-evolution APIs but lacked a supported CLI entrypoint.
- Boundary 0.3.0 exposes `boundary contracts authorize`.
- Boundary 0.3.0 documents `boundary verify` as the closure command, but that command is defective for contract evolution.
- The original missing-entrypoint report must not be treated as a separate current defect without checking the installed CLI.

### Planned resolution

1. Confirm the current CLI accepts and correctly authorizes contract-evolution operations.
2. Review command help, argument validation, blocking diagnostic output, and skill instructions.
3. Use the repaired verification path from task 1 to complete the public contract-evolution workflow.
4. Add or extend end-to-end CLI coverage if authorization entrypoint coverage is insufficient.
5. Check that installation through mise provides the same commands and guidance.
6. Document version requirements for affected downstream projects.
7. Do not add a redundant second contract-evolution API or CLI command merely to work around verification dispatch.

### Acceptance criteria

- Contract-evolution authorization and verification are both available through documented installed CLI commands.
- An operator does not need runtime bootstrap code, manual operation-record edits, or undocumented native-service invocations.
- Skill instructions, CLI help, and runtime behavior agree.
- The historical 0.2.0 limitation is identified as superseded once the complete workflow is confirmed.

## 4. Release and downstream validation

Perform after the corresponding fixes have passed focused verification.

1. Run all relevant unit, CLI, integration, and regression tests.
2. Run `mise exec -- boundary integration check` and the repository hygiene checks.
3. Keep changed canonical code and documentation files at or below 250 lines; split responsibilities where necessary.
4. Confirm generated `.agents/` and `.specify/` state is not used as canonical source.
5. Prepare an appropriately versioned Boundary release using the documented mise-managed distribution procedure.
6. Validate the released executable in a clean downstream installation.
7. Confirm the previously failing contract-evolution CLI workflow works against active Spec Kit change bookkeeping.
8. Confirm Feature 005's interface-contract ownership can be established without weakening its implementation write scope.
9. Ensure dependent implementation begins only after contract evolution has verified and a fresh implementation authorization succeeds.
10. Record resolved items and any remaining downstream migration instructions before clearing this TODO.

## Scope and exclusions

- Do not edit `../gui-auto2/BOUNDARY-FEEDBACK.md`.
- Do not reopen or reconstruct already verified operation records.
- Do not introduce a new Boundary-owned lock format to address the observation that the mise lock names a tag rather than an immutable commit. Source identity and locking are governed by `docs/spec-distribution.md`; assess any separate reproducibility concern against that specification before treating it as another defect.
- Do not alter Feature 005 calibration or launcher behavior as part of fixing Boundary itself.
- Do not treat successful Boundary verification as proof of downstream application acceptance.
- Do not edit persistent contracts during an implementation operation.

The immediate next implementation unit should address task 1. Tasks 2 and 3 may then be resolved independently, with task 3 reusing the verified CLI closure path rather than duplicating it.
