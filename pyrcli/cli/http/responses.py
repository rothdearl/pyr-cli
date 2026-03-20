"""Utilities for parsing and validating HTTP response bodies."""

import requests

from pyrcli.cli import ErrorReporter
from .types import JsonValue


def get_json_body(response: requests.Response, *, allowed_types: tuple[type[JsonValue], ...] = (dict, list),
                  on_error: ErrorReporter) -> JsonValue | None:
    """
    Return the decoded JSON body of ``response``.

    - Calls ``on_error(message)`` and returns ``None`` if decoding fails or the value is not one of ``allowed_types``.
    """
    try:
        json_value = response.json()
    except ValueError:
        on_error("response body is not valid json")
        return None

    if not isinstance(json_value, allowed_types):
        on_error("unexpected json value type")
        return None

    return json_value


__all__ = ("get_json_body",)
