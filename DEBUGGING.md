# Boundary upstream troubleshooting

## Goal

Resolve the failure reported in BOUNDARY-UPSTREAM-REPORT where `boundary status` and `boundary authorize --task T022` fail with `selectedTaskIds must be an array`.

## Confirmed failure path

The current direct task-selection path is not the source of the reported scalar-selection failure:

- the product CLI uses argparse `action="append"` for `--task`, so one `--task T022` reaches the adapter as a one-element sequence;
- the Spec Kit command handler also normalizes a direct string input to a one-element tuple;
- native authorization persists `ImplementationAuthorization.selected_task_ids` through `OperationRecord`;
- the canonical record writer always serializes `selectedTaskIds` as a JSON array.

The exact message `selectedTaskIds must be an array` comes from operation-record decoding in `src/boundary/authorization/codec.py`.

Both reported commands read existing current operation evidence:

- `boundary status` reads `.git/boundary/current.json` directly through `read_authorization_handoff`;
- a fresh authorization reads the current record through predecessor handling before it can replace a verified epoch.

This explains why both status and an otherwise valid single-task authorization fail before a new T022 record can be installed.

## Root cause

Version-1 persisted operation evidence from an earlier Boundary build can have task selection in a non-canonical historical shape. A missing `selectedTaskIds` field and a scalar single-task value both previously fail immediately in the decoder even though immutable task evidence is sufficient to validate the historical selection.

That compatibility failure makes a verified predecessor unreadable and therefore blocks both the read-only status query and successor authorization.

## Fix

Operation-record decoding now accepts only two additional unambiguous historical forms:

- missing `selectedTaskIds`: derive implementation selection from the immutable task evidence already stored in the record, or use an empty selection for contract evolution;
- scalar string `selectedTaskIds`: normalize it to one selected task identity.

The existing `OperationRecord` validation remains authoritative after normalization. It still requires selected implementation identities to exactly match the stored task evidence, so malformed or widening historical evidence remains rejected.

Canonical serialization is unchanged and always emits `selectedTaskIds` as an array.

## Regression coverage

Added focused coverage for:

- deriving a multi-task historical selection when `selectedTaskIds` is absent;
- reading status from a legacy single-task scalar selection;
- replacing a verified legacy predecessor with a fresh single-task authorization;
- rejecting a scalar selection that does not exactly match immutable task evidence.

## Validation remaining

Run the focused compatibility, status, Spec Kit authorization, and runtime-projection tests, then the contract check, full suite, diff check, changed-file line-count check, and Git status check from `dev-scripts.include`.

If those checks remain green, the upstream defect is fixed and this file should be deleted.
