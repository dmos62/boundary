from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[1]
PRESET_ROOT = REPO_ROOT / "integration" / "speckit-preset"
EXTENSION_ROOT = REPO_ROOT / "integration" / "speckit"
AGENT_ADAPTERS_ROOT = REPO_ROOT / "adapters"
CANONICAL_SKILLS_ROOT = REPO_ROOT / "skills"
WORKFLOW_OVERLAY_PATH = EXTENSION_ROOT / "workflow-overlay.yml"
CODEX_SKILLS_DIR = Path(".agents") / "skills"
SPECKIT_VERSION = "1.0.10"


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


def skill_file(root: Path, command: str) -> Path:
    return root / CODEX_SKILLS_DIR / command.replace(".", "-") / "SKILL.md"


def skill_body(content: str) -> str:
    """Return semantic command body, ignoring Codex registrar serialization."""

    lines = content.splitlines(keepends=True)
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                content = "".join(lines[index + 1 :])
                break

    content = content.lstrip("\r\n")
    body_lines = content.splitlines(keepends=True)
    if (
        body_lines
        and body_lines[0].startswith("# Speckit ")
        and body_lines[0].strip().endswith(" Skill")
    ):
        content = "".join(body_lines[1:]).lstrip("\r\n")
    return content


def run_command(
    root: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    return subprocess.run(
        list(args),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=process_env,
    )


def require_success(testcase, result: subprocess.CompletedProcess[str]) -> None:
    testcase.assertEqual(
        0,
        result.returncode,
        result.stdout + "\n" + result.stderr,
    )


def init_project(testcase, root: Path, integration: str = "codex") -> None:
    require_success(testcase, run_command(root, "git", "init", "-q"))
    require_success(
        testcase,
        run_command(
            root,
            "specify",
            "init",
            "--here",
            "--force",
            "--non-interactive",
            "--ignore-agent-tools",
            "--script",
            "sh",
            "--integration",
            integration,
        ),
    )


def active_integration(root: Path) -> str | None:
    state = json.loads(
        (root / ".specify" / "integration.json").read_text(encoding="utf-8")
    )
    return state.get("default_integration") or state.get("integration")
