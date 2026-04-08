"""Runtime distribution metadata for Pyr-CLI."""

from importlib.metadata import PackageNotFoundError, version
from typing import Final


def _get_version() -> str:
    """Return the installed distribution version for pyr-cli, or ``"0+unknown"`` if the package is not installed."""
    try:
        return version("pyr-cli")
    except PackageNotFoundError:
        return "0+unknown"


__version__: Final[str] = _get_version()
