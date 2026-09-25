#!/usr/bin/env bash
set -euo pipefail

readonly SPECKIT_VERSION="1.0.10"
readonly SPECKIT_TAG="v${SPECKIT_VERSION}"
readonly ACTIVE_INTEGRATION="codex"
readonly EXTENSION_ID="boundary"
readonly PRESET_ID="boundary"
readonly WORKFLOW_ID="speckit"
readonly WORKFLOW_OVERLAY_ID="boundary"
readonly WORKFLOW_OVERLAY_PRIORITY="10"
readonly CODEX_SKILL_ADAPTER="adapters/codex/materialize.py"
readonly BOUNDARY_RUNTIME_DIR=".specify/boundary-runtime"
readonly INSTALL_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

ACTION="install"
SOURCE="."
TEMP_ROOT=""
SOURCE_ROOT=""

fail() {
  printf 'install: %s\n' "$*" >&2
  exit 1
}

require_command() {
  local command_name="$1"
  command -v "$command_name" >/dev/null 2>&1 ||
    fail "required command not found: ${command_name}"
}

selected_speckit_script_type() {
  local options_path=".specify/init-options.json"

  [[ -f "$options_path" ]] || return 0

  uv run --no-project python - "$options_path" <<'PY'
import json
from pathlib import Path
import sys

path = Path(sys.argv[1])
try:
    options = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(
        f"install: invalid Spec Kit init options at {path}: {exc}",
        file=sys.stderr,
    )
    raise SystemExit(1)

script_type = options.get("script")
if script_type is None:
    raise SystemExit(0)
if not isinstance(script_type, str):
    print(
        f"install: invalid Spec Kit script mode in {path}: expected a string",
        file=sys.stderr,
    )
    raise SystemExit(1)

print(script_type)
PY
}

require_speckit_script_runtime() {
  local script_type

  script_type="$(selected_speckit_script_type)" ||
    fail "could not determine the configured Spec Kit script mode"

  case "$script_type" in
    ""|sh|py)
      ;;
    ps)
      command -v pwsh >/dev/null 2>&1 ||
        fail "Spec Kit PowerShell script mode requires pwsh; install PowerShell or select a supported Spec Kit script mode before installing Boundary"
      ;;
    *)
      fail "unsupported Spec Kit script mode: ${script_type}"
      ;;
  esac
}

speckit_matches_pin() {
  command -v specify >/dev/null 2>&1 &&
    specify --version 2>&1 |
      grep -Eq "(^|[^0-9])${SPECKIT_VERSION//./\\.}([^0-9]|$)"
}

ensure_install_prerequisites() {
  require_command git
  require_command uv
  require_command codex
  require_speckit_script_runtime

  if ! speckit_matches_pin; then
    uv tool install specify-cli --force \
      --from "git+https://github.com/github/spec-kit.git@${SPECKIT_TAG}"
  fi
  speckit_matches_pin ||
    fail "Spec Kit ${SPECKIT_VERSION} could not be installed"
}

check_install_prerequisites() {
  require_command git
  require_command uv
  require_command codex
  require_speckit_script_runtime
  require_command specify
  speckit_matches_pin ||
    fail "Spec Kit ${SPECKIT_VERSION} is required"
}

source "$INSTALL_SCRIPT_DIR/install-source.sh"
source "$INSTALL_SCRIPT_DIR/install-host.sh"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/install.sh [--source <directory|archive>]
  bash scripts/install.sh --check
  bash scripts/install.sh --remove

This script installs from already materialized local Boundary source.

The --source option accepts a local directory or local archive. Local archive
input is supported for Boundary development; the downstream consumer delegates
installation using its validated Boundary checkout as the local source.

Downstream repositories should run scripts/consumer.py from a clean Boundary
checkout whose revision matches boundary.lock.json. Neither install.sh nor the
downstream consumer retrieves or reconstructs Boundary source.
EOF
}

cleanup() {
  if [[ -n "$TEMP_ROOT" && -d "$TEMP_ROOT" ]]; then
    rm -rf "$TEMP_ROOT"
  fi
}
trap cleanup EXIT

while (($#)); do
  case "$1" in
    --source)
      (($# >= 2)) || fail "--source requires a value"
      SOURCE="$2"
      shift 2
      ;;
    --check)
      ACTION="check"
      shift
      ;;
    --remove)
      ACTION="remove"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

case "$ACTION" in
  install)
    ensure_install_prerequisites
    materialize_source "$SOURCE"
    require_source_tree
    install_adapter
    ;;
  check)
    check_install_prerequisites
    check_adapter
    ;;
  remove)
    remove_adapter
    ;;
esac
