"""Installation of Boundary-owned Spec Kit and Codex integration state."""

from __future__ import annotations

from pathlib import Path
import sys

from .errors import IntegrationError
from .host_runtime import (
    ACTIVE_INTEGRATION,
    EXTENSION_ID,
    PRESET_ID,
    WORKFLOW_ID,
    WORKFLOW_OVERLAY_ID,
    WORKFLOW_OVERLAY_PRIORITY,
    active_integration,
    require_base_prerequisites,
    require_script_runtime,
    run,
    script_override,
    selected_script_mode,
)


def install_host(root: Path, assets: Path) -> None:
    """Materialize Boundary-owned integration through supported host lifecycle."""

    require_base_prerequisites(root)
    override = script_override()
    _ensure_codex_project(root, override)
    _install_adapter_assets(root, assets)
    _materialize_boundary_skills(root, assets)


def _ensure_codex_project(
    root: Path,
    override: str | None,
) -> None:
    if not (root / ".specify").is_dir():
        args = [
            "specify",
            "init",
            "--here",
            "--force",
            "--non-interactive",
            "--ignore-agent-tools",
            "--integration",
            ACTIVE_INTEGRATION,
        ]
        if override is not None:
            args.extend(["--script", override])
        run(root, args)
    else:
        current = active_integration(root)
        if current != ACTIVE_INTEGRATION:
            args = ["specify", "integration", "switch", ACTIVE_INTEGRATION]
            if override is not None:
                args.extend(["--script", override])
            run(root, args)
        elif (
            override is not None
            and selected_script_mode(root) != override
        ):
            run(
                root,
                [
                    "specify",
                    "integration",
                    "upgrade",
                    ACTIVE_INTEGRATION,
                    "--force",
                    "--script",
                    override,
                ],
            )

    mode = selected_script_mode(root)
    if override is not None and mode != override:
        raise IntegrationError(
            f"Spec Kit did not select requested script mode: {override}"
        )
    require_script_runtime(mode)


def _install_adapter_assets(root: Path, assets: Path) -> None:
    extension = assets / "integration" / "speckit"
    preset = assets / "integration" / "speckit-preset"
    overlay = extension / "workflow-overlay.yml"
    for path in (extension / "extension.yml", preset / "preset.yml", overlay):
        if not path.is_file():
            raise IntegrationError(
                f"installed Boundary asset is missing: {path}"
            )

    run(
        root,
        [
            "specify",
            "extension",
            "add",
            str(extension),
            "--dev",
            "--force",
        ],
    )

    if (root / ".specify" / "presets" / PRESET_ID).exists():
        run(root, ["specify", "preset", "remove", PRESET_ID])
    run(
        root,
        [
            "specify",
            "preset",
            "add",
            "--dev",
            str(preset),
            "--priority",
            WORKFLOW_OVERLAY_PRIORITY,
        ],
    )

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
    run(
        root,
        [
            "specify",
            "workflow",
            "overlay",
            "add",
            str(overlay),
            "--priority",
            WORKFLOW_OVERLAY_PRIORITY,
        ],
    )


def _materialize_boundary_skills(root: Path, assets: Path) -> None:
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
        ],
    )
