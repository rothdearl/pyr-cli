"""Public API for the http package."""

from .client import (
    delete,
    get,
    post,
    put,
    set_timeout,
)
from .responses import decode_json_body
from .types import (
    JsonArray,
    JsonObject,
    JsonScalar,
    JsonValue,
    KeyValuePairs,
    MultipartFiles,
    QueryParameters,
)
from .upload import open_multipart_file

__all__ = (
    # client
    "delete",
    "get",
    "post",
    "put",
    "set_timeout",

    # responses
    "decode_json_body",

    # types
    "JsonArray",
    "JsonObject",
    "JsonScalar",
    "JsonValue",
    "KeyValuePairs",
    "MultipartFiles",
    "QueryParameters",

    # upload
    "open_multipart_file",
)
