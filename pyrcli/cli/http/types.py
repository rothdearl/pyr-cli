"""Type aliases for HTTP requests and JSON values."""

from collections.abc import Mapping
from typing import Any, BinaryIO, Final

#: Decoded JSON array.
type JsonArray = list[Any]

#: Decoded JSON object.
type JsonObject = dict[str, Any]

#: Decoded JSON scalar value (string, number, boolean, or null).
type JsonScalar = str | int | float | bool | None

#: Any decoded JSON value.
type JsonType = JsonArray | JsonObject | JsonScalar

#: String-to-string mapping for HTTP headers and similar key-value data.
type KeyValuePairs = Mapping[str, str]

#: Mapping of form field names to (filename, binary file object) tuples for multipart uploads.
type MultipartFiles = Mapping[str, tuple[str, BinaryIO]]

#: String-to-string mapping of URL query parameters.
type QueryParameters = Mapping[str, str]

__all__: Final[tuple[str, ...]] = (
    "JsonArray",
    "JsonObject",
    "JsonScalar",
    "JsonType",
    "KeyValuePairs",
    "MultipartFiles",
    "QueryParameters",
)
