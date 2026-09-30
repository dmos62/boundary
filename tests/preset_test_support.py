from __future__ import annotations

import json
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PRESET_ROOT = REPO_ROOT / "integration" / "speckit-preset"
EXTENSION_ROOT = REPO_ROOT / "integration" / "speckit"
AGENT_ADAPTERS_ROOT = REPO_ROOT / "adapters"
CANONICAL_SKILLS_ROOT = REPO_ROOT / "skills"
BOUNDARY_SOURCE_ROOT = REPO_ROOT / "src" / "boundary"
SCRIPTS_ROOT = REPO_ROOT / "scripts"
WORKFLOW_OVERLAY_PATH = EXTENSION_ROOT / "workflow-overlay.yml"
BOOTSTRAP_PATH = REPO_ROOT / "scripts" / "bootstrap.sh"
INSTALLER_PATH = REPO_ROOT / "scripts" / "install.sh"
INSTALL_SOURCE_PATH = REPO_ROOT / "scripts" / "install-source.sh"
INSTALL_HOST_PATH = REPO_ROOT / "scripts" / "install-host.sh"
CODEX_SKILLS_DIR = Path(".agents") / "skills"
INSTALLED_RUNTIME_PATH = (
    Path(".specify") / "extensions" / "boundary" / "scripts" / "adapter_gate.py"
)
INSTALLED_BOUNDARY_RUNTIME = (
    Path(".specify") / "boundary-runtime" / "boundary" / "__init__.py"
)

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


def archive_source(destination: Path) -> Path:
    archive = destination / "boundary-source.tar.gz"
    prefix = "boundary-source"
    with tarfile.open(archive, "w:gz") as package:
        for source, relative in (
            (EXTENSION_ROOT, "integration/speckit"),
            (PRESET_ROOT, "integration/speckit-preset"),
            (AGENT_ADAPTERS_ROOT, "adapters"),
            (CANONICAL_SKILLS_ROOT, "skills"),
            (BOUNDARY_SOURCE_ROOT, "src/boundary"),
            (SCRIPTS_ROOT, "scripts"),
        ):
            package.add(source, arcname=f"{prefix}/{relative}")
    return archive


def write_consumer_fixture(testcase, root: Path) -> Path:
    source = root / "src" / "app.py"
    source.parent.mkdir(parents=True)
    source.write_text('VALUE = "before"\n', encoding="utf-8")

    contract = root / "contracts" / "app.contract.md"
    contract.parent.mkdir(parents=True)
    contract.write_text(
        "---\n"
        "schema: boundary.contract/v1\n"
        "id: app\n"
        "owns:\n"
        "  - src/app.py\n"
        "applies_to: []\n"
        "depends_on: []\n"
        "---\n"
        "## Invariants\n\n"
        "- The application value remains a string.\n",
        encoding="utf-8",
    )

    feature_dir = root / "specs" / "001-runtime"
    feature_dir.mkdir(parents=True)
    (feature_dir / "plan.md").write_text(
        "# Plan\n\nImplementation target: `src/app.py`\n",
        encoding="utf-8",
    )
    (feature_dir / "tasks.md").write_text(
        "# Tasks\n\n"
        "- [ ] T001 [US1] Update application value\n"
        "  Writes: `src/app.py`\n",
        encoding="utf-8",
    )

    for key, value in (
        ("user.email", "tests@example.invalid"),
        ("user.name", "Boundary Tests"),
    ):
        require_success(testcase, run_command(root, "git", "config", key, value))
    require_success(testcase, run_command(root, "git", "add", "-A"))
    require_success(
        testcase,
        run_command(root, "git", "commit", "-q", "-m", "consumer fixture baseline"),
    )
    return feature_dir


def run_installed_gate(
    root: Path,
    feature_dir: Path,
    stage: str,
    task_ids: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    env = {
        "SPECIFY_FEATURE_DIRECTORY": feature_dir.relative_to(root).as_posix(),
    }
    if stage == "authorize":
        if not task_ids:
            raise ValueError("authorize gate requires explicit task_ids")
        env["BOUNDARY_TASK_IDS"] = json.dumps(list(task_ids))

    return run_command(
        root,
        "uv",
        "run",
        "--no-project",
        "python",
        str(INSTALLED_RUNTIME_PATH),
        stage,
        env=env,
    )
