"""Base class for command-line programs that process text files and streams."""

import io
import os
import sys
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import Final, final, override

from .ansi import RESET
from .cli_program import CLIProgram
from .io import InputFile, iter_stdin_file_names, read_text_files
from .terminal import stdin_is_redirected


class TextProgram(CLIProgram, ABC):
    """
    Base class for command-line programs that process text files and streams.

    Attributes:
        encoding: Encoding used when reading text files (default: ``"utf-8"``).
    """

    def __init__(self, *, name: str, error_exit_code: int = 1) -> None:
        """Initialize a new instance."""
        super().__init__(name=name, error_exit_code=error_exit_code)

        self.encoding: str = "utf-8"

    def _invoke_redirected_input(self) -> None:
        """Invoke ``handle_redirected_input()`` when redirected standard input contains data."""
        # Use peek() to detect piped input without consuming it.
        # Fall back to readlines() when the underlying buffer is not a BufferedReader.
        stdin_buffer = getattr(sys.stdin, "buffer", None)

        if isinstance(stdin_buffer, io.BufferedReader):
            if stdin_buffer.peek():
                self.handle_redirected_input(sys.stdin)
        elif input_lines := sys.stdin.readlines():
            self.handle_redirected_input(input_lines)

    def _process_text_files(self, file_names: Iterable[str]) -> list[str]:
        """
        Process each file and return the names of successfully processed files.

        - Skips unreadable files and reports errors via print_error().
        """
        processed_files = []

        for input_file in read_text_files(file_names, encoding=self.encoding, on_error=self.print_error):
            try:
                self.process_text_stream(input_file)
                processed_files.append(input_file.file_name)
            except UnicodeDecodeError:
                self.print_error(f"{input_file.file_name!r}: unable to read with {self.encoding!r}")

        return processed_files

    def _route_redirected_input(self) -> list[str]:
        """Process redirected input and return the names of successfully processed files."""
        processed_files = []

        if self.args.stdin_files:
            processed_files.extend(self._process_text_files(iter_stdin_file_names()))
        else:
            self._invoke_redirected_input()

        # Process any additional file arguments.
        if self.args.files:
            processed_files.extend(self._process_text_files(self.args.files))

        return processed_files

    @final
    def execute(self) -> None:
        """Route input sources and process them using the configured handlers."""
        processed_files = []

        if stdin_is_redirected():
            processed_files.extend(self._route_redirected_input())
        elif self.args.files:
            processed_files.extend(self._process_text_files(self.args.files))
        else:
            self.handle_terminal_input()

        self.post_execute(processed_files)

    @final
    def format_file_header(self, file_name: str, *, file_name_style: str, colon_style: str) -> str:
        """Return a styled ``file_name:`` header, or ``"(standard input):"`` when the file name is empty."""
        display_name = os.path.relpath(file_name) if file_name else "(standard input)"

        if self.print_color:
            return (
                f"{file_name_style}"
                f"{display_name}"
                f"{colon_style}:"
                f"{RESET}"
            )

        return f"{display_name}:"

    @abstractmethod
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        ...

    @abstractmethod
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        ...

    @override
    def initialize_runtime_state(self) -> None:
        """
        Initialize internal state derived from parsed options.

        - Sets encoding to ``iso-8859-1`` when ``--latin1`` is enabled.
        """
        super().initialize_runtime_state()

        self.encoding = "iso-8859-1" if getattr(self.args, "latin1", False) else "utf-8"

    def post_execute(self, processed_files: Sequence[str]) -> None:
        """Run post-execution logic after all input processing completes."""
        pass  # Optional hook; no action by default.

    @abstractmethod
    def process_text_stream(self, input_file: InputFile) -> None:
        """Process the text stream from ``input_file``."""
        ...

    @final
    def should_print_file_header(self) -> bool:
        """Return ``True`` if file headers should be printed."""
        return not getattr(self.args, "no_file_name", False)


__all__: Final[tuple[str, ...]] = ("TextProgram",)
