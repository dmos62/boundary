Downstream consumer feedback remains the active task.

The available feedback contains three reports:

- The 2026-09-25 10:56 UTC PowerShell failure targeted Boundary revision e43163557886c326ab4add0438af4b60b9586f37 and is historical. The operator later migrated Spec Kit itself to Bash, and the current installer already preserves or explicitly transitions the selected Spec Kit script mode.
- The 2026-09-25 13:49 UTC `setup-plan.sh --json` `BRANCH` value is a minor Spec Kit metadata ambiguity. It did not reach Boundary authorization and does not presently justify changing Boundary behavior.
- The 2026-09-25 14:12 UTC report targets revision 65a989e86d1668444d4dd33034534b12b0ae5d31 and identifies the active Boundary defect: the Spec Kit adapter still invokes `.specify/scripts/powershell/check-prerequisites.ps1` through `pwsh` after the project has selected `"script": "sh"`.

Next implementation iteration:

- inspect `docs/spec-change-adapter.md`, the native contracts applying to the Spec Kit adapter, the adapter implementation containing `spec_kit_adapter.py`, and its adapter gate;
- reproduce the active Bash-mode authorization failure against current source before changing behavior;
- add focused regression coverage proving authorization resolves the active feature through the configured Spec Kit script runtime without requiring PowerShell for a Bash project;
- make adapter runtime selection follow `.specify/init-options.json` consistently with installer/runtime semantics, while preserving supported `sh`, `ps`, and `py` modes;
- run the focused Spec Kit adapter tests plus the real Spec Kit lifecycle coverage;
- update focused documentation only if the implementation exposes a contract or lifecycle detail not already stated.

Do not change downstream source-checkout distribution semantics while fixing this adapter defect.
