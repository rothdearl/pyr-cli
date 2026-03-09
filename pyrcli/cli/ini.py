"""Utilities for reading and querying INI configuration files."""

import configparser
import json
from typing import Any, Final

from .types import ErrorReporter

# Shared across all callers; reflects the most recently loaded configuration.
_config: configparser.ConfigParser = configparser.ConfigParser()

# String values that are considered falsy.
_falsy_values: Final[frozenset[str]] = frozenset({"0", "false", "off", "n", "no"})

# String values that are considered truthy.
_truthy_values: Final[frozenset[str]] = frozenset({"1", "on", "true", "y", "yes"})


def get_bool_option(section: str, option: str) -> bool | None:
    """
    Return a boolean value parsed from the option.

    - Uses ``"false"`` if the option is missing or empty.
    - Returns ``True`` or ``False`` for recognized truthy or falsy values.
    - Returns ``None`` if the value is neither truthy nor falsy.
    """
    value = get_str_option_with_fallback(section, option, fallback="false").lower()

    if value in _falsy_values:
        return False

    if value in _truthy_values:
        return True

    return None


def get_dict_option(section: str, option: str) -> dict[str, Any] | None:
    """
    Return a dictionary parsed from the option.

    - Uses ``"{}"`` if the option is missing or empty.
    - Returns the decoded dictionary when parsing succeeds.
    - Returns ``None`` if decoding fails or the value is not a dictionary.
    """
    value = get_str_option_with_fallback(section, option, fallback="{}")

    try:
        dict_value = json.loads(value)
    except json.JSONDecodeError:
        return None

    return dict_value if isinstance(dict_value, dict) else None


def get_float_option(section: str, option: str) -> float | None:
    """
    Return a floating-point value parsed from the option.

    - Uses ``"0.0"`` if the option is missing or empty.
    - Returns the parsed floating-point value when conversion succeeds.
    - Returns ``None`` if the value cannot be parsed.
    """
    value = get_str_option_with_fallback(section, option, fallback="0.0")

    try:
        return float(value)
    except ValueError:
        return None


def get_int_option(section: str, option: str) -> int | None:
    """
    Return an integer value parsed from the option.

    - Uses ``"0"`` if the option is missing or empty.
    - Returns the parsed integer value when conversion succeeds.
    - Returns ``None`` if the value cannot be parsed.
    """
    value = get_str_option_with_fallback(section, option, fallback="0")

    try:
        return int(value)
    except ValueError:
        return None


def get_str_option(section: str, option: str) -> str:
    """Return a string value, using ``""`` if the option is missing or empty."""
    return get_str_option_with_fallback(section, option, fallback="")


def get_str_option_with_fallback(section: str, option: str, *, fallback: str) -> str:
    """Return a string value, using ``fallback`` if the option is missing or empty."""
    return _config.get(section, option, fallback=fallback) or fallback


def get_str_options(section: str, option: str, *, separator: str = ",") -> list[str]:
    """Return string values split on a separator, trimming whitespace and ignoring empty entries."""
    value = get_str_option_with_fallback(section, option, fallback="")

    return [entry for part in value.split(separator) if (entry := part.strip())]


def has_defaults() -> bool:
    """Return ``True`` if the DEFAULT section contains any options."""
    return bool(_config.defaults())


def has_sections() -> bool:
    """Return ``True`` if any non-default sections exist."""
    return bool(_config.sections())


def is_empty() -> bool:
    """Return ``True`` if the configuration is empty."""
    return not has_defaults() and not has_sections()


def read_options(path: str, *, clear_previous: bool = True, on_error: ErrorReporter) -> bool:
    """
    Read options from a configuration file.

    - Clears previously loaded options before reading when ``clear_previous`` is ``True``.
    - Invokes ``on_error(message)`` if the file cannot be read or parsed.
    - Errors reported: missing file, permission denied, invalid configuration file, other OS read errors.
    - Returns ``True`` on success.
    - If reading fails after clearing, the configuration remains empty.
    """
    try:
        with open(path, mode="rt", encoding="utf-8") as f:
            if clear_previous:
                _config.clear()

            _config.read_file(f)
    except (configparser.Error, OSError) as error:
        match error:
            case FileNotFoundError():
                on_error(f"{path!r}: no such file or directory")
            case PermissionError():
                on_error(f"{path!r}: permission denied")
            case configparser.Error():
                on_error(f"{path!r}: invalid configuration file")
            case OSError():
                on_error(f"{path!r}: unable to read file")

        return False

    return True


__all__: Final[tuple[str, ...]] = (
    "get_bool_option",
    "get_dict_option",
    "get_float_option",
    "get_int_option",
    "get_str_option",
    "get_str_option_with_fallback",
    "get_str_options",
    "has_defaults",
    "has_sections",
    "is_empty",
    "read_options",
)
