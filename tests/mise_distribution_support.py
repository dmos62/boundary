from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_TREES = ("src", "integration", "adapters", "skills")


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


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


def make_boundary_source(root: Path) -> tuple[Path, str]:
    # Match the supported mise pipx Git locator shape. The backend recognizes
    # explicit Git URLs by their .git suffix before resolving `latest`.
    source = root / "boundary-source.git"
    source.mkdir()
    shutil.copy2(REPO_ROOT / "pyproject.toml", source / "pyproject.toml")
    ignored = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
    for relative in PACKAGE_TREES:
        shutil.copytree(
            REPO_ROOT / relative,
            source / relative,
            ignore=ignored,
        )

    pyproject = source / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    marker = 'boundary = "boundary.cli:main"\n'
    if marker not in content:
        raise AssertionError("Boundary console entry point is missing")
    pyproject.write_text(
        content.replace(
            marker,
            marker
            + 'boundary-test-source-id = "boundary._distribution_source:main"\n',
            1,
        ),
        encoding="utf-8",
    )
    _write_source_identity(source, "source-a")
    _git_init(source)
    return source, _git_head(source)


def advance_boundary_source(source: Path) -> str:
    _write_source_identity(source, "source-b")
    added = run_command(
        source,
        "git",
        "add",
        "src/boundary/_distribution_source.py",
    )
    if added.returncode != 0:
        raise AssertionError(added.stderr)
    committed = run_command(source, "git", "commit", "-q", "-m", "source b")
    if committed.returncode != 0:
        raise AssertionError(committed.stdout + committed.stderr)
    return _git_head(source)


def write_downstream_project(root: Path, source: Path) -> str:
    root.mkdir()
    _git_init(root, commit=False)
    source_url = source.as_uri()
    if not source_url.endswith(".git"):
        raise AssertionError(
            "Boundary Git fixture locator must use a .git suffix"
        )
    tool = f"pipx:git+{source_url}"
    (root / "mise.toml").write_text(
        'min_version = "2026.9.0"\n\n'
        "[tools]\n"
        f'"{tool}" = "latest"\n',
        encoding="utf-8",
    )
    return tool


def mise_env(root: Path, state: Path) -> dict[str, str]:
    home = state / "home"
    home.mkdir(parents=True, exist_ok=True)
    return {
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(state / "xdg-config"),
        "XDG_DATA_HOME": str(state / "xdg-data"),
        "XDG_CACHE_HOME": str(state / "xdg-cache"),
        "XDG_STATE_HOME": str(state / "xdg-state"),
        "MISE_DATA_DIR": str(state / "data"),
        "MISE_CACHE_DIR": str(state / "cache"),
        "MISE_STATE_DIR": str(state / "state"),
        "MISE_TRUSTED_CONFIG_PATHS": str(root),
        "MISE_YES": "1",
        "MISE_JOBS": "1",
        "UV_CACHE_DIR": str(state / "uv-cache"),
    }


def _write_source_identity(source: Path, value: str) -> None:
    (source / "src" / "boundary" / "_distribution_source.py").write_text(
        "def main() -> None:\n"
        f"    print({value!r})\n",
        encoding="utf-8",
    )


def _git_init(root: Path, *, commit: bool = True) -> None:
    initialized = run_command(root, "git", "init", "-q")
    if initialized.returncode != 0:
        raise AssertionError(initialized.stderr)
    for key, value in (
        ("user.email", "tests@example.invalid"),
        ("user.name", "Boundary Tests"),
    ):
        configured = run_command(root, "git", "config", key, value)
        if configured.returncode != 0:
            raise AssertionError(configured.stderr)
    if commit:
        added = run_command(root, "git", "add", "-A")
        if added.returncode != 0:
            raise AssertionError(added.stderr)
        created = run_command(root, "git", "commit", "-q", "-m", "source a")
        if created.returncode != 0:
            raise AssertionError(created.stdout + created.stderr)


def _git_head(root: Path) -> str:
    result = run_command(root, "git", "rev-parse", "HEAD")
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return result.stdout.strip()
