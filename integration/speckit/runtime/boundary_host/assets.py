"""Locate immutable integration assets shipped with the Boundary package."""

from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

from .errors import IntegrationError

_DISTRIBUTION = "boundary-cli"
_MARKER = "boundary_assets/integration/speckit/extension.yml"


def asset_root() -> Path:
    """Return the installed or editable-development Boundary asset root."""

    installed = _installed_asset_root()
    if installed is not None:
        return installed

    source_root = Path(__file__).resolve().parents[4]
    if (source_root / "integration" / "speckit" / "extension.yml").is_file():
        return source_root

    raise IntegrationError(
        "installed Boundary integration assets are unavailable"
    )


def _installed_asset_root() -> Path | None:
    try:
        packaged_files = distribution(_DISTRIBUTION).files or ()
    except PackageNotFoundError:
        return None

    for item in packaged_files:
        if item.as_posix() == _MARKER:
            marker = Path(item.locate())
            root = marker.parents[2]
            if root.is_dir():
                return root
    return None
