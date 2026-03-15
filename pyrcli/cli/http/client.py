"""Helpers for sending HTTP DELETE, GET, POST, and PUT requests."""

import json
from enum import StrEnum
from typing import Callable, Final

import requests

from .types import JsonArray, JsonObject, KeyValuePairs, MultipartFiles, QueryParameters
from .upload import multipart_file


class _HTTPMethod(StrEnum):
    """HTTP request method."""
    DELETE = "DELETE"
    GET = "GET"
    POST = "POST"
    PUT = "PUT"


# HTTP method to internal request function dispatch table.
_REQUEST_DISPATCH: Final[dict[_HTTPMethod, Callable[..., requests.Response]]] = {
    _HTTPMethod.DELETE: requests.delete,
    _HTTPMethod.GET: requests.get,
    _HTTPMethod.POST: requests.post,
    _HTTPMethod.PUT: requests.put,
}

# Module-wide request timeout in seconds; use set_timeout() to change.
_request_timeout: float = 15.0


def _build_request_headers(*, data: JsonArray | JsonObject | None = None, files: MultipartFiles | None = None,
                           serialize_to_json: bool = True, auth_headers: KeyValuePairs | None = None) -> KeyValuePairs:
    """
    Return HTTP request headers.

    - Always sets ``Accept: application/json``.
    - Sets ``Content-Type`` based on ``data``, ``files``, and ``serialize_to_json``:

      - For JSON bodies (no files, ``serialize_to_json=True``), uses ``application/json``.
      - For form bodies (no files, ``serialize_to_json=False``), uses ``application/x-www-form-urlencoded; charset=utf-8``.
      - For multipart/form-data (files provided), leaves ``Content-Type`` unset for ``requests`` to populate.
    - Merges ``auth_headers`` into the returned headers when provided.
    """
    headers = {"Accept": "application/json"}

    # Let requests set multipart/form-data Content-Type with boundary for files.
    if files is None and data is not None:
        if serialize_to_json:
            headers["Content-Type"] = "application/json"
        else:
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"

    if auth_headers is not None:
        headers.update(auth_headers)

    return headers


def _execute_request(*, method: _HTTPMethod, url: str, params: QueryParameters | None = None,
                     data: JsonArray | JsonObject | None = None, files: MultipartFiles | None = None,
                     headers: KeyValuePairs, raise_on_error: bool) -> requests.Response:
    """
    Send the HTTP request and return the response.

    - Dispatches to the corresponding ``requests`` function for ``method``.
    - Uses the module-wide request timeout (configurable via ``set_timeout``).
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    request_function = _REQUEST_DISPATCH[method]
    response = request_function(url=url, params=params, data=data, files=files, headers=headers,
                                timeout=_request_timeout)

    if raise_on_error:
        response.raise_for_status()

    return response


def _serialize_json_body(*, data: JsonArray | JsonObject | None, files: MultipartFiles | None,
                         enabled: bool) -> JsonArray | JsonObject | str | None:
    """Serialize ``data`` to JSON when ``enabled`` and no files are provided."""
    if files is None and data is not None and enabled:
        return json.dumps(data)

    return data


def delete(url: str, *, params: QueryParameters | None = None, auth_headers: KeyValuePairs | None = None,
           raise_on_error: bool = False) -> requests.Response:
    """
    Send a DELETE request and return the response.

    - Adds ``Accept: application/json`` to the request headers.
    - Merges ``auth_headers`` into the request headers when provided.
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    headers = _build_request_headers(auth_headers=auth_headers)

    return _execute_request(method=_HTTPMethod.DELETE, url=url, params=params, headers=headers,
                            raise_on_error=raise_on_error)


def get(url: str, *, params: QueryParameters | None = None, auth_headers: KeyValuePairs | None = None,
        raise_on_error: bool = False) -> requests.Response:
    """
    Send a GET request and return the response.

    - Adds ``Accept: application/json`` to the request headers.
    - Merges ``auth_headers`` into the request headers when provided.
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    headers = _build_request_headers(auth_headers=auth_headers)

    return _execute_request(method=_HTTPMethod.GET, url=url, params=params, headers=headers,
                            raise_on_error=raise_on_error)


def post(url: str, *, params: QueryParameters | None = None, data: JsonArray | JsonObject | None = None,
         files: MultipartFiles | None = None, serialize_to_json: bool = True, auth_headers: KeyValuePairs | None = None,
         raise_on_error: bool = False) -> requests.Response:
    """
    Send a POST request and return the response.

    - Serializes ``data`` to JSON and sets JSON headers when ``serialize_to_json`` is ``True`` and ``files`` is not provided.
    - When ``files`` is provided, sends a multipart/form-data request and lets ``requests`` set the content type.
    - Adds ``Accept: application/json`` to the request headers.
    - Merges ``auth_headers`` into the request headers when provided.
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    headers = _build_request_headers(data=data, files=files, serialize_to_json=serialize_to_json,
                                     auth_headers=auth_headers)
    payload = _serialize_json_body(data=data, files=files, enabled=serialize_to_json)

    return _execute_request(method=_HTTPMethod.POST, url=url, params=params, data=payload, files=files, headers=headers,
                            raise_on_error=raise_on_error)


def put(url: str, *, params: QueryParameters | None = None, data: JsonArray | JsonObject | None = None,
        files: MultipartFiles | None = None, serialize_to_json: bool = True, auth_headers: KeyValuePairs | None = None,
        raise_on_error: bool = False) -> requests.Response:
    """
    Send a PUT request and return the response.

    - Serializes ``data`` to JSON and sets JSON headers when ``serialize_to_json`` is ``True`` and ``files`` is not provided.
    - When ``files`` is provided, sends a multipart/form-data request and lets ``requests`` set the content type.
    - Adds ``Accept: application/json`` to the request headers.
    - Merges ``auth_headers`` into the request headers when provided.
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    headers = _build_request_headers(data=data, files=files, serialize_to_json=serialize_to_json,
                                     auth_headers=auth_headers)
    payload = _serialize_json_body(data=data, files=files, enabled=serialize_to_json)

    return _execute_request(method=_HTTPMethod.PUT, url=url, params=params, data=payload, files=files, headers=headers,
                            raise_on_error=raise_on_error)


def put_file(url: str, *, file_path: str, field_name: str = "file", auth_headers: KeyValuePairs | None = None,
             raise_on_error: bool = False) -> requests.Response:
    """
    Upload a file using a multipart/form-data PUT request and return the response.

    - Uses ``field_name`` as the multipart/form-data field name (default: ``"file"``).
    - Merges ``auth_headers`` into the request headers when provided.
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    with multipart_file(file_path, field_name=field_name) as files:
        return put(url, files=files, auth_headers=auth_headers, raise_on_error=raise_on_error)


def set_timeout(timeout: float) -> None:
    """Set the module-wide HTTP request timeout in seconds; ignored if ``timeout`` is non-positive."""
    if timeout <= 0:
        return

    global _request_timeout
    _request_timeout = timeout


__all__: Final[tuple[str, ...]] = (
    "delete",
    "get",
    "post",
    "put",
    "put_file",
    "set_timeout",
)
