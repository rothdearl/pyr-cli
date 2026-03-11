"""HTTP request helpers for DELETE, GET, POST, and PUT operations built on ``requests``."""

import json
from enum import StrEnum
from typing import Callable, Final

import requests

from .types import JsonType, KeyValuePairs, MultipartFiles, QueryParameters
from .upload import multipart_file


class _Methods(StrEnum):
    """HTTP methods used for internal request dispatch."""
    DELETE = "DELETE"
    GET = "GET"
    POST = "POST"
    PUT = "PUT"


# HTTP method to request function dispatch table.
_REQUESTS_FUNCTIONS: Final[dict[_Methods, Callable[..., requests.Response]]] = {
    _Methods.DELETE: requests.delete,
    _Methods.GET: requests.get,
    _Methods.POST: requests.post,
    _Methods.PUT: requests.put,
}

# Module-wide request timeout in seconds; configure via set_timeout().
_timeout: float = 15.0


def _build_request_headers(*, data: JsonType = None, files: MultipartFiles | None = None,
                           serialize_to_json: bool = True, auth_headers: KeyValuePairs | None = None) -> KeyValuePairs:
    """
    Return HTTP request headers for the client.

    - Always sets ``Accept: application/json``.
    - Sets ``Content-Type`` based on ``data``, ``files``, and ``serialize_to_json``:
        - For JSON bodies (no files, ``serialize_to_json=True``), uses ``application/json``.
        - For form bodies (no files, ``serialize_to_json=False``), uses ``application/x-www-form-urlencoded; charset=utf-8``.
        - For multipart (files provided), leaves ``Content-Type`` unset for ``requests`` to populate.
    - Merges ``auth_headers`` into the returned headers when provided.
    """
    headers = {"Accept": "application/json"}

    # Let requests set multipart Content-Type with boundary for files.
    if files is None and data is not None:
        if serialize_to_json:
            headers["Content-Type"] = "application/json"
        else:
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"

    if auth_headers is not None:
        headers.update(auth_headers)

    return headers


def _execute_request(*, method: _Methods, url: str, params: QueryParameters | None = None, data: JsonType = None,
                     files: MultipartFiles | None = None, headers: KeyValuePairs,
                     raise_on_error: bool) -> requests.Response:
    """
    Execute the HTTP request and return the ``requests.Response``.

    - Dispatches to the corresponding ``requests`` function for ``method``.
    - Uses the module-wide default request timeout (configurable via ``set_timeout``).
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    request_function = _REQUESTS_FUNCTIONS[method]
    response = request_function(url=url, params=params, data=data, files=files, headers=headers, timeout=_timeout)

    if raise_on_error:
        response.raise_for_status()

    return response


def _serialize_request_body(*, data: JsonType, files: MultipartFiles | None, serialize_to_json: bool) -> JsonType:
    """Serialize the request body payload when conditions are met, or return ``data`` unchanged."""
    if files is None and isinstance(data, dict) and serialize_to_json:
        return json.dumps(data)

    return data


def delete(url: str, *, params: QueryParameters | None = None,
           auth_headers: KeyValuePairs | None = None, raise_on_error: bool = False) -> requests.Response:
    """
    Send a DELETE request and return the response.

    - Adds ``Accept: application/json`` to the request headers.
    - Merges ``auth_headers`` into the request headers when provided.
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    headers = _build_request_headers(auth_headers=auth_headers)

    return _execute_request(method=_Methods.DELETE, url=url, params=params, headers=headers,
                            raise_on_error=raise_on_error)


def get(url: str, *, params: QueryParameters | None = None,
        auth_headers: KeyValuePairs | None = None, raise_on_error: bool = False) -> requests.Response:
    """
    Send a GET request and return the response.

    - Adds ``Accept: application/json`` to the request headers.
    - Merges ``auth_headers`` into the request headers when provided.
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    headers = _build_request_headers(auth_headers=auth_headers)

    return _execute_request(method=_Methods.GET, url=url, params=params, headers=headers, raise_on_error=raise_on_error)


def post(url: str, *, params: QueryParameters | None = None, data: JsonType = None, files: MultipartFiles | None = None,
         serialize_to_json: bool = True, auth_headers: KeyValuePairs | None = None,
         raise_on_error: bool = False) -> requests.Response:
    """
    Send a POST request and return the response.

    - When ``serialize_to_json`` is ``True`` and ``files`` is not provided, serializes mapping payloads to JSON and sets JSON headers.
    - When ``files`` is provided, sends a multipart request and lets ``requests`` set the multipart content type.
    - Adds ``Accept: application/json`` to the request headers.
    - Merges ``auth_headers`` into the request headers when provided.
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    headers = _build_request_headers(data=data, files=files, serialize_to_json=serialize_to_json,
                                     auth_headers=auth_headers)
    payload = _serialize_request_body(data=data, files=files, serialize_to_json=serialize_to_json)

    return _execute_request(method=_Methods.POST, url=url, params=params, data=payload, files=files, headers=headers,
                            raise_on_error=raise_on_error)


def put(url: str, *, params: QueryParameters | None = None, data: JsonType = None, files: MultipartFiles | None = None,
        serialize_to_json: bool = True, auth_headers: KeyValuePairs | None = None,
        raise_on_error: bool = False) -> requests.Response:
    """
    Send a PUT request and return the response.

    - When ``serialize_to_json`` is ``True`` and ``files`` is not provided, serializes mapping payloads to JSON and sets JSON headers.
    - When ``files`` is provided, sends a multipart request and lets ``requests`` set the multipart content type.
    - Adds ``Accept: application/json`` to the request headers.
    - Merges ``auth_headers`` into the request headers when provided.
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    headers = _build_request_headers(data=data, files=files, serialize_to_json=serialize_to_json,
                                     auth_headers=auth_headers)
    payload = _serialize_request_body(data=data, files=files, serialize_to_json=serialize_to_json)

    return _execute_request(method=_Methods.PUT, url=url, params=params, data=payload, files=files, headers=headers,
                            raise_on_error=raise_on_error)


def put_file(url: str, *, file_path: str, field_name: str = "file", auth_headers: KeyValuePairs | None = None,
             raise_on_error: bool = False) -> requests.Response:
    """
    Send a PUT request that uploads a file via multipart/form-data.

    - Sends the file as multipart/form-data.
    - Adds ``Accept: application/json`` to the request headers.
    - Merges ``auth_headers`` into the request headers when provided.
    - Calls ``response.raise_for_status()`` when ``raise_on_error`` is ``True``.
    """
    with multipart_file(file_path, field_name=field_name) as files:
        return put(url, files=files, auth_headers=auth_headers, raise_on_error=raise_on_error)


def set_timeout(timeout: float) -> None:
    """Set the module-wide HTTP request timeout in seconds, affecting all subsequent requests."""
    if timeout <= 0:
        raise ValueError("http request timeout must be greater than 0.")

    global _timeout
    _timeout = timeout


__all__: Final[tuple[str, ...]] = (
    "delete",
    "get",
    "post",
    "put",
    "put_file",
    "set_timeout",
)
