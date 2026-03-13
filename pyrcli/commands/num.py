"""Implements a program that numbers lines from files and prints them to standard output."""

import argparse
import sys
from collections.abc import Iterable
from typing import Final, NoReturn, override

from pyrcli.cli import TextProgram, text
from pyrcli.cli.ansi import ForegroundColors, RESET
from pyrcli.cli.io import InputFile

# Format-spec alignment prefixes keyed by --number-format value.
_FORMAT_PREFIXES: Final[dict[str, str]] = {
    "ln": "<",  # Left-aligned
    "rn": ">",  # Right-aligned
    "rz": "0>",  # Zero-padded, right-aligned
}


class _Styles:
    """Namespace for ANSI styling constants."""
    COLON: Final[str] = ForegroundColors.BRIGHT_CYAN
    FILE_NAME: Final[str] = ForegroundColors.BRIGHT_MAGENTA
    LINE_NUMBER: Final[str] = ForegroundColors.BRIGHT_GREEN


class Num(TextProgram):
    """Command implementation for numbering lines from files and printing them to standard output."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="num", buffer_stdin=True)

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="number lines in FILES",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)
        blank_group = parser.add_mutually_exclusive_group()

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        parser.add_argument("-b", "--number-nonblank", action="store_true", help="number nonblank lines")
        parser.add_argument("--number-start", default=1, help="start numbering at N (default: 1; N >= 0)", metavar="N",
                            type=int)
        parser.add_argument("-w", "--number-width", default=6, help="pad line numbers to width N (default: 6; N >= 1)",
                            metavar="N", type=int)
        parser.add_argument("--number-format", choices=("ln", "rn", "rz"), default="rn",
                            help="format line numbers (ln=left, rn=right, rz=zero-padded; default: rn)")
        parser.add_argument("--number-separator", default="\t",
                            help="separate line numbers and output lines with SEP (default: <tab>)", metavar="SEP")
        blank_group.add_argument("-s", "--squeeze-blank", action="store_true", help="suppress repeated blank lines")
        blank_group.add_argument("--no-blank", action="store_true", help="suppress blank lines")
        parser.add_argument("-H", "--no-file-name", action="store_true", help="suppress file name prefixes")
        parser.add_argument("--color", choices=("on", "off"), default="on",
                            help="use color for file names and line numbers (default: on)")
        parser.add_argument("--latin1", action="store_true", help="read FILES as latin-1 (default: utf-8)")
        parser.add_argument("--stdin-files", action="store_true", help="read FILES from standard input (one per line)")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        self.print_file_header(file_name="")
        self.number_lines(input_lines)

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        self.number_lines(sys.stdin)

    @override
    def normalize_options(self) -> None:
        """Apply derived defaults and adjust option values for consistent internal use."""
        # Suppress file headers when standard input is the only source.
        if not self.args.files and not self.args.stdin_files:
            self.args.no_file_name = True

        # Decode escape sequences in --number-separator.
        try:
            self.args.number_separator = self.args.number_separator.encode().decode("unicode_escape")
        except UnicodeDecodeError:
            self.print_error_and_exit("--number-separator contains an invalid escape sequence")

    def number_lines(self, lines: Iterable[str]) -> None:
        """Number lines and print them to standard output."""
        blank_line_count = 0
        format_prefix = _FORMAT_PREFIXES[self.args.number_format]
        line_number = self.args.number_start - 1

        for line in text.iter_normalized_lines(lines):
            print_number = True

            if not line:
                blank_line_count += 1

                if self.should_suppress_blank_line(blank_line_count):
                    continue

                if self.args.number_nonblank:
                    print_number = False
            else:
                blank_line_count = 0

            if print_number:
                line_number += 1
                line = self.render_line_number(line, line_number, format_prefix=format_prefix)

            print(line)

    def print_file_header(self, file_name: str) -> None:
        """Print the file header for ``file_name``."""
        if self.should_print_file_header():
            print(self.format_file_header(file_name, file_name_style=_Styles.FILE_NAME, colon_style=_Styles.COLON))

    @override
    def process_text_stream(self, input_file: InputFile) -> None:
        """Process the text stream for a single input file."""
        self.print_file_header(input_file.file_name)
        self.number_lines(input_file.text_stream)

    def render_line_number(self, line: str, line_number: int, *, format_prefix: str) -> str:
        """Prefix a formatted line number to the line."""
        if self.print_color:
            return (
                f"{_Styles.LINE_NUMBER}"
                f"{line_number:{format_prefix}{self.args.number_width}}"
                f"{RESET}"
                f"{self.args.number_separator}"
                f"{line}"
            )

        return (
            f"{line_number:{format_prefix}{self.args.number_width}}"
            f"{self.args.number_separator}"
            f"{line}"
        )

    def should_suppress_blank_line(self, blank_line_count: int) -> bool:
        """Return ``True`` if a blank line should be suppressed."""
        if self.args.no_blank:
            return True

        if self.args.squeeze_blank and blank_line_count > 1:
            return True

        return False

    @override
    def validate_option_ranges(self) -> None:
        """Validate that option values fall within their allowed numeric or logical ranges."""
        if self.args.number_start < 0:
            self.print_error_and_exit("--number-start must be >= 0")

        if self.args.number_width < 1:
            self.print_error_and_exit("--number-width must be >= 1")


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Num().run()


if __name__ == "__main__":
    raise SystemExit(main())
