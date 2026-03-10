"""Utilities for generating multipart file mappings for HTTP uploads."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Final

from .types import MultipartFiles


@contextmanager
def multipart_file(file_path: str, *, field_name: str = "file") -> Iterator[MultipartFiles]:
    """
    Yield a mapping for uploading a file via HTTP multipart.

    - Opens the file in binary mode.
    - Yields a mapping suitable for the ``files`` parameter of an HTTP multipart upload.
    - Closes the file when the context exits.
    """
    path = Path(file_path)

    with path.open("rb") as file:
        yield {field_name: (path.name, file)}


__all__: Final[tuple[str, ...]] = ("multipart_file",)
