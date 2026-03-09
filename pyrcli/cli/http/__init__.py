"""Public API for the http package."""

from typing import Final

from .client import (
    delete,
    get,
    post,
    put,
    put_file,
    set_timeout,
)
from .responses import parse_json_body
from .types import (
    JsonArray,
    JsonObject,
    JsonScalar,
    JsonType,
    KeyValuePairs,
    MultipartFiles,
    QueryParameters,
)
from .upload import multipart_file

__all__: Final[tuple[str, ...]] = (
    # client
    "delete",
    "get",
    "post",
    "put",
    "put_file",
    "set_timeout",

    # response
    "parse_json_body",

    # upload
    "multipart_file",

    # types
    "JsonArray",
    "JsonObject",
    "JsonScalar",
    "JsonType",
    "KeyValuePairs",
    "MultipartFiles",
    "QueryParameters",
)
