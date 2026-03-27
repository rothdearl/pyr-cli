"""Utilities for reading environment variables. """

import os

from .types import ErrorReporter


def get_env_str(key: str, default: str | None = None, *, trim: bool = True) -> str | None:
    """Return the value of environment variable ``key``, or ``default`` if unset or empty after trimming."""
    value = os.getenv(key)

    if value is None:
        return default

    if trim:
        value = value.strip()

    return value or default


def get_required_env_str(key: str, *, trim: bool = True, on_error: ErrorReporter) -> str | None:
    """
    Return the value of environment variable ``key``, or ``None`` if missing or empty.

    - Removes surrounding whitespace from the value when ``trim`` is enabled.
    - Calls ``on_error(message)`` and returns ``None`` when ``key`` is unset or empty.
    """
    value = get_env_str(key, trim=trim)

    if value is None:
        on_error(f"environment variable {key!r} must be set")

    return value


__all__ = (
    "get_env_str",
    "get_required_env_str",
)
