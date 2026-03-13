"""Implements a program that prints the first part of files."""

import argparse
import sys
from collections import deque
from collections.abc import Iterable
from typing import Final, NoReturn, override

from pyrcli.cli import TextProgram, text
from pyrcli.cli.ansi import ForegroundColors
from pyrcli.cli.io import InputFile


class _Styles:
    """Namespace for ANSI styling constants."""
    COLON: Final[str] = ForegroundColors.BRIGHT_CYAN
    FILE_NAME: Final[str] = ForegroundColors.BRIGHT_MAGENTA


class Peek(TextProgram):
    """Command implementation for printing the first part of files."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="peek", buffer_stdin=True)

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="print the first part of FILES",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        parser.add_argument("-n", "--lines", default=10,
                            help="print the first N lines, or all but the last N if N < 0 (default: 10)", metavar="N",
                            type=int)
        parser.add_argument("-H", "--no-file-name", action="store_true", help="suppress file name prefixes")
        parser.add_argument("--color", choices=("on", "off"), default="on",
                            help="use color for file names (default: on)")
        parser.add_argument("--latin1", action="store_true", help="read FILES as latin-1 (default: utf-8)")
        parser.add_argument("--stdin-files", action="store_true", help="read FILES from standard input (one per line)")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        self.print_file_header(file_name="")
        self.print_lines(input_lines)

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        self.args.lines = abs(self.args.lines)  # Normalize --lines before reading from standard input.
        self.print_lines(sys.stdin)

    @override
    def normalize_options(self) -> None:
        """Apply derived defaults and adjust option values for consistent internal use."""
        # Suppress file headers when standard input is the only source.
        if not self.args.files and not self.args.stdin_files:
            self.args.no_file_name = True

    def print_file_header(self, file_name: str) -> None:
        """Print the file header for ``file_name``."""
        if self.should_print_file_header():
            print(self.format_file_header(file_name, file_name_style=_Styles.FILE_NAME, colon_style=_Styles.COLON))

    def print_lines(self, lines: Iterable[str]) -> None:
        """Print lines to standard output."""
        # --lines is positive or zero: print the first N lines.
        if self.args.lines >= 0:
            for index, line in enumerate(text.iter_normalized_lines(lines)):
                if index >= self.args.lines:
                    break

                print(line)

            return

        # --lines is negative: print all but the last |N| lines.
        buffer = deque(maxlen=-self.args.lines)

        for line in text.iter_normalized_lines(lines):
            if len(buffer) == buffer.maxlen:
                print(buffer.popleft())

            buffer.append(line)

    @override
    def process_text_stream(self, input_file: InputFile) -> None:
        """Process the text stream for a single input file."""
        self.print_file_header(input_file.file_name)
        self.print_lines(input_file.text_stream)


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Peek().run()


if __name__ == "__main__":
    raise SystemExit(main())
