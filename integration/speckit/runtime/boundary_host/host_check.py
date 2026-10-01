"""Health checking and removal of Boundary-owned host integration state."""

from __future__ import annotations

from pathlib import Path
import shutil
import sys

from .errors import IntegrationError
from .host_runtime import (
    ACTIVE_INTEGRATION,
    EXTENSION_ID,
    PRESET_ID,
    WORKFLOW_ID,
    WORKFLOW_OVERLAY_ID,
    active_integration,
    require_base_prerequisites,
    require_command,
    require_script_runtime,
    run,
    selected_script_mode,
)


def check_host(root: Path, assets: Path) -> None:
    """Validate Boundary-owned generated integration and host prerequisites."""

    require_base_prerequisites(root)
    require_script_runtime(selected_script_mode(root))
    if active_integration(root) != ACTIVE_INTEGRATION:
        raise IntegrationError(
            f"Spec Kit active integration must be {ACTIVE_INTEGRATION!r}"
        )

    installed_extension = (
        root / ".specify" / "extensions" / EXTENSION_ID
    )
    canonical_extension = assets / "integration" / "speckit"
    _require_same_file(
        installed_extension / "extension.yml",
        canonical_extension / "extension.yml",
        root,
    )
    _require_asset_tree(
        installed_extension / "commands",
        canonical_extension / "commands",
        root,
    )
    _require_asset_tree(
        root / ".specify" / "presets" / PRESET_ID,
        assets / "integration" / "speckit-preset",
        root,
    )
    _require_same_file(
        (
            root
            / ".specify"
            / "workflows"
            / "overlays"
            / WORKFLOW_ID
            / f"{WORKFLOW_OVERLAY_ID}.yml"
        ),
        assets / "integration" / "speckit" / "workflow-overlay.yml",
        root,
    )

    for skill in (
        "speckit-boundary-authorize",
        "speckit-boundary-verify",
    ):
        _require_skill(root, skill)

    _check_boundary_skills(root, assets)

    tasks_skill = _require_skill(root, "speckit-tasks")
    if "## Boundary Write Scope" not in tasks_skill.read_text(
        encoding="utf-8"
    ):
        raise IntegrationError(
            "Spec Kit tasks skill is missing Boundary scope guidance"
        )

    _check_workflow_overlay(root)


def remove_host(root: Path) -> None:
    """Remove Boundary-owned generated host integration."""

    if (root / ".specify").is_dir():
        require_command("specify")
        run(
            root,
            [
                "specify",
                "workflow",
                "overlay",
                "remove",
                WORKFLOW_ID,
                WORKFLOW_OVERLAY_ID,
            ],
            allow_failure=True,
        )

        if (root / ".specify" / "presets" / PRESET_ID).exists():
            run(root, ["specify", "preset", "remove", PRESET_ID])
        if (root / ".specify" / "extensions" / EXTENSION_ID).exists():
            run(
                root,
                ["specify", "extension", "remove", EXTENSION_ID, "--force"],
            )

    _remove_boundary_skills(root)


def _require_asset_tree(
    installed: Path,
    canonical: Path,
    root: Path,
) -> None:
    if not canonical.is_dir():
        raise IntegrationError(
            f"installed Boundary asset directory is missing: {canonical}"
        )
    for source in canonical.rglob("*"):
        if source.is_file():
            relative = source.relative_to(canonical)
            _require_same_file(installed / relative, source, root)


def _require_same_file(
    installed: Path,
    canonical: Path,
    root: Path,
) -> None:
    try:
        matches = installed.read_bytes() == canonical.read_bytes()
    except OSError as exc:
        raise IntegrationError(
            "Boundary generated integration state is missing or unreadable: "
            f"{installed.relative_to(root)}"
        ) from exc
    if not matches:
        raise IntegrationError(
            "Boundary generated integration state is stale: "
            f"{installed.relative_to(root)}"
        )


def _check_boundary_skills(root: Path, assets: Path) -> None:
    """Validate materialized Boundary skills against canonical package assets."""

    materializer = assets / "adapters" / "codex" / "materialize.py"
    if not materializer.is_file():
        raise IntegrationError(
            "installed Codex Boundary skill materializer is missing"
        )

    run(
        root,
        [
            sys.executable,
            str(materializer),
            "--source-root",
            str(assets),
            "--project-root",
            str(root),
            "--check",
        ],
    )


def _check_workflow_overlay(root: Path) -> None:
    listing = run(
        root,
        ["specify", "workflow", "overlay", "list", WORKFLOW_ID],
    ).stdout
    if WORKFLOW_OVERLAY_ID not in listing:
        raise IntegrationError("Boundary workflow overlay is not installed")

    resolved = run(
        root,
        ["specify", "workflow", "resolve", WORKFLOW_ID],
    ).stdout
    for step in ("boundary-authorize", "boundary-verify"):
        if step not in resolved:
            raise IntegrationError(
                f"resolved Spec Kit workflow is missing structural step: {step}"
            )


def _require_skill(root: Path, name: str) -> Path:
    path = root / ".agents" / "skills" / name / "SKILL.md"
    if not path.is_file():
        raise IntegrationError(
            f"expected Codex skill is missing: {path.relative_to(root)}"
        )
    return path


def _remove_boundary_skills(root: Path) -> None:
    for name in (
        "speckit-boundary-authorize",
        "speckit-boundary-verify",
        "boundary-scope",
        "boundary-implement",
        "boundary-contracts",
    ):
        path = root / ".agents" / "skills" / name
        if path.is_symlink() or path.is_file():
            path.unlink(missing_ok=True)
        elif path.is_dir():
            shutil.rmtree(path)
