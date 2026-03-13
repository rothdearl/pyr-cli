"""Utilities for reading and writing text files and streams."""

import os
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Final, NamedTuple, TextIO

from .text import iter_nonempty_lines, iter_normalized_lines, strip_trailing_newline
from .types import ErrorReporter


class InputFile(NamedTuple):
    """
    Information about a file being read.

    Attributes:
        file_name: File name (normalized by the caller).
        text_stream: Open text stream for the file, valid only until the next iteration.
    """
    file_name: str
    text_stream: TextIO


def iter_descendant_paths(root: Path, max_depth: int = sys.maxsize) -> Iterator[Path]:
    """
    Yield descendant paths under ``root`` whose depth is less than or equal to ``max_depth``.

    - Depth is measured relative to ``root`` (depth 1 is an immediate child).
    - The ``root`` path itself is not yielded.
    - Subdirectories deeper than ``max_depth`` are not traversed.
    """
    root_depth = len(root.parts)

    for dir_path, dir_names, file_names in os.walk(top=root, topdown=True, followlinks=False):
        current_path = Path(dir_path)
        depth = len(current_path.parts) - root_depth

        # Prune subdirectories to prevent descent beyond max_depth.
        if depth >= max_depth:
            dir_names[:] = []
            continue

        for name in dir_names:
            yield current_path / name

        for name in file_names:
            yield current_path / name


def iter_stdin_file_names() -> Iterator[str]:
    """Yield normalized, non-empty file names from standard input."""
    yield from iter_nonempty_lines(sys.stdin)


def read_text_files(file_names: Iterable[str], *, encoding: str, on_error: ErrorReporter) -> Iterator[InputFile]:
    """
    Yield a ``InputFile`` for each readable file in ``file_names``.

    - Each yielded ``InputFile.text_stream`` is valid only until the next iteration.
    - Invokes ``on_error(message)`` for file-related errors; processing continues with the next file.
    - Reports: directory path, missing file, unknown encoding, permission denied, and other OS read errors.
    """
    for file_name in iter_normalized_lines(file_names):
        try:
            if os.path.isdir(file_name):
                on_error(f"{file_name!r}: is a directory")
                continue

            with open(file_name, mode="rt", encoding=encoding) as text_stream:
                yield InputFile(file_name, text_stream)
        except FileNotFoundError:
            on_error(f"{file_name!r}: no such file or directory")
        except LookupError:
            on_error(f"{file_name!r}: unknown encoding {encoding!r}")
        except PermissionError:
            on_error(f"{file_name!r}: permission denied")
        except OSError:
            on_error(f"{file_name!r}: unable to read")


def write_text_file(file_name: str, *, lines: Iterable[str], encoding: str, on_error: ErrorReporter) -> None:
    """
    Write lines to a file, normalizing each line to end with exactly one newline.

    - Invokes ``on_error(message)`` for file-related errors.
    - Reports: unknown encoding, permission denied, encoding failures, and other OS write errors.
    """
    try:
        with open(file_name, mode="wt", encoding=encoding) as f:
            for line in lines:
                f.write(strip_trailing_newline(line) + "\n")
    except LookupError:
        on_error(f"{file_name!r}: unknown encoding {encoding!r}")
    except PermissionError:
        on_error(f"{file_name!r}: permission denied")
    except UnicodeEncodeError:
        on_error(f"{file_name!r}: unable to write with {encoding!r}")
    except OSError:
        on_error(f"{file_name!r}: unable to write")


__all__: Final[tuple[str, ...]] = (
    "InputFile",
    "iter_descendant_paths",
    "iter_stdin_file_names",
    "read_text_files",
    "write_text_file",
)
