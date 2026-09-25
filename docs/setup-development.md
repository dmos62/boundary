# Boundary Development Setup

This guide is for contributors working on Boundary source itself.

Downstream project installation is documented separately in [setup-downstream.md](setup-downstream.md).

## Bootstrap the source repository

Run:

    bash scripts/bootstrap.sh

Development bootstrap deliberately reinitializes Spec Kit through its supported `specify init --here --force` lifecycle before reinstalling Boundary. Boundary does not pass a script mode by default, so the pinned Spec Kit selects its platform default: `sh` on Linux/macOS and `ps` on Windows.

This regeneration repairs development checkouts that were initialized by older Boundary bootstrap code that always selected PowerShell.

To deliberately use a non-default script mode, set `BOUNDARY_SPECKIT_SCRIPT` for the bootstrap run:

    BOUNDARY_SPECKIT_SCRIPT=ps bash scripts/bootstrap.sh

Accepted values are `sh`, `ps`, and `py`. An explicit `ps` selection requires `pwsh` on `PATH`.

Check an existing development installation with:

    bash scripts/bootstrap.sh --check

The check validates the currently selected Spec Kit runtime; it does not change script mode.

## Reinstall local source directly

For development iterations, run:

    bash scripts/install.sh --source .

The source installer preserves an existing Spec Kit script mode. Set `BOUNDARY_SPECKIT_SCRIPT=sh|ps|py` only when intentionally asking Spec Kit to change that mode through its supported integration lifecycle.

The source installer accepts an already materialized local Boundary directory or local archive.

It does not fetch unchecked remote Boundary source. Downstream repositories do not reconstruct Boundary source from the lock. Operators supply a clean Boundary checkout at the exact revision recorded in `boundary.lock.json` and invoke that checkout's `scripts/consumer.py`.

## Core checks

Validate native contracts:

    PYTHONPATH=src uv run --no-project python -m boundary contracts check

Run native Boundary tests:

    PYTHONPATH=src uv run --no-project \
      python -m unittest discover -s tests -p 'test_native_*.py'

Run Spec Kit adapter tests:

    PYTHONPATH=src:integration/speckit/scripts uv run --no-project \
      python -m unittest discover -s tests -p 'test_spec_kit_adapter*.py'

Run downstream lock tests:

    PYTHONPATH=src uv run --no-project \
      python -m unittest discover -s tests -p 'test_consumer*.py'

Run script-mode lifecycle tests:

    uv run --no-project python -m unittest tests.test_install_host_script_mode

## Source and generated state

Canonical Boundary source includes `src/boundary/`, canonical skills, concrete adapters, integration source, scripts, contracts, and documentation.

Generated `.specify/` installation state and materialized `.agents/skills/` outputs are not replacements for that source.

The Boundary source repository therefore uses local-source development procedures rather than treating its own downstream consumer lock as its development bootstrap.
