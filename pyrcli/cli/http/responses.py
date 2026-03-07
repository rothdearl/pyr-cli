"""Utilities for parsing and validating HTTP response bodies."""

from typing import Final

import requests

from pyrcli.cli import ErrorReporter, JsonArray, JsonObject


def parse_json_body(response: requests.Response, *, on_error: ErrorReporter) -> JsonArray | JsonObject | None:
    """
    Return the JSON body from ``response``, or ``None`` if parsing fails.

    - Invokes ``on_error(message)`` if the response body cannot be decoded as JSON.
    - Returns ``None`` if the response body is not a JSON object or array.
    """
    try:
        parsed_json = response.json()
    except requests.JSONDecodeError:
        on_error("unable to decode json from response")
        return None

    if not isinstance(parsed_json, (dict, list)):
        on_error("unexpected response format")
        return None

    return parsed_json


__all__: Final[tuple[str, ...]] = ("parse_json_body",)
