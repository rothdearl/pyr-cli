"""Utilities for parsing and validating HTTP response bodies."""

from typing import Final

import requests

from pyrcli.cli import ErrorReporter
from .types import JsonType


def parse_json_body(response: requests.Response, *, allowed_types: tuple[type[JsonType], ...] = (dict, list),
                    on_error: ErrorReporter) -> JsonType | None:
    """
    Return the decoded JSON body from ``response``.

    - Invokes ``on_error(message)`` and returns ``None`` if:

      - The body cannot be decoded as JSON.
      - The decoded value is not one of ``allowed_types``.
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


__all__: Final[tuple[str, ...]] = ("parse_json_body",)
