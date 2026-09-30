"""CLI rendering for current Boundary authorization state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TextIO

from boundary.authorization import read_authorization_handoff


def run_status(
    repository_root: Path,
    output: TextIO,
) -> int:
    """Render the compact current authorization handoff as JSON."""

    handoff = read_authorization_handoff(repository_root)
    document = None if handoff is None else handoff.to_document()
    print(
        json.dumps(
            document,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        file=output,
    )
    return 0
