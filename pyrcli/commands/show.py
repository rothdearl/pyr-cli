"""Implements a program that prints files to standard output."""

import argparse
import sys
from collections.abc import Iterable, Sequence
from typing import Final, NoReturn, override

from pyrcli.cli import TextProgram, text
from pyrcli.cli.ansi import ForegroundColors, RESET
from pyrcli.cli.io import InputFile


class _Styles:
    """Namespace for ANSI styling constants."""
    COLON: Final[str] = ForegroundColors.BRIGHT_CYAN
    END_MARKER: Final[str] = ForegroundColors.BRIGHT_BLUE
    FILE_NAME: Final[str] = ForegroundColors.BRIGHT_MAGENTA
    LINE_NUMBER: Final[str] = ForegroundColors.BRIGHT_GREEN
    SPACE_MARKER: Final[str] = ForegroundColors.BRIGHT_CYAN
    TAB_MARKER: Final[str] = ForegroundColors.BRIGHT_CYAN


class _Whitespace:
    """Namespace for whitespace replacement constants."""
    END_MARKER: Final[str] = "$"
    SPACE_MARKER: Final[str] = "·"
    TAB_MARKER: Final[str] = ">···"
    TRAILING_SPACE_MARKER: Final[str] = "~"


class Show(TextProgram):
    """Command implementation for printing files to standard output."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="show")

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="print FILES to standard output",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        parser.add_argument("-s", "--start", default=1, help="start at line N (N < 0 counts from end; N != 0)",
                            metavar="N", type=int)
        parser.add_argument("-l", "--max-lines", default=sys.maxsize, help="print first N lines (N >= 1)", metavar="N",
                            type=int)
        parser.add_argument("-n", "--line-numbers", action="store_true", help="number lines")
        parser.add_argument("--ends", action="store_true",
                            help=f"display '{_Whitespace.END_MARKER}' at end of each line")
        parser.add_argument("--spaces", action="store_true",
                            help=f"display spaces as '{_Whitespace.SPACE_MARKER}' and trailing spaces as '{_Whitespace.TRAILING_SPACE_MARKER}'")
        parser.add_argument("--tabs", action="store_true", help=f"display tab characters as '{_Whitespace.TAB_MARKER}'")
        parser.add_argument("-H", "--no-file-name", action="store_true", help="suppress file name prefixes")
        parser.add_argument("--color", choices=("on", "off"), default="on",
                            help="use color for file names, line numbers, and whitespace (default: on)")
        parser.add_argument("--latin1", action="store_true", help="read FILES as latin-1 (default: utf-8)")
        parser.add_argument("--stdin-files", action="store_true", help="read FILES from standard input (one per line)")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    def get_line_range(self, lines: Sequence[str]) -> tuple[int, int]:
        """
        Return the start and end line numbers for printing.

        - Negative ``--start`` values count from the end of ``lines``.
        """
        line_start = self.args.start if self.args.start > 0 else len(lines) + self.args.start + 1
        line_end = min(len(lines), line_start + self.args.max_lines - 1)

        return line_start, line_end

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        lines = list(input_lines)  # Materialize to a list; print_lines requires a Sequence to compute line range.

        self.print_file_header(file_name="")
        self.print_lines(lines)

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        self.print_lines(sys.stdin.readlines())  # print_lines requires a Sequence to compute line range.

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

    def print_lines(self, lines: Sequence[str]) -> None:
        """Print lines to standard output, applying numbering and whitespace rendering."""
        line_start, line_end = self.get_line_range(lines)
        padding = len(str(line_end))

        for line_number, line in enumerate(text.iter_normalized_lines(lines), start=1):
            if line_start <= line_number <= line_end:
                rendered = line

                if self.args.spaces:
                    rendered = self.render_spaces(rendered)

                if self.args.tabs:
                    rendered = self.render_tabs(rendered)

                if self.args.ends:
                    rendered = self.render_ends(rendered)

                if self.args.line_numbers:
                    rendered = self.render_line_number(rendered, line_number, padding=padding)

                print(rendered)

    @override
    def process_input_file(self, input_file: InputFile) -> None:
        """Process the text stream from ``input_file``."""
        self.print_file_header(input_file.file_name)
        self.print_lines(input_file.text_stream.readlines())

    def render_ends(self, line: str) -> str:
        """Append a visible end-of-line marker to the line."""
        if self.use_color:
            return (
                f"{line}"
                f"{_Styles.END_MARKER}"
                f"{_Whitespace.END_MARKER}"
                f"{RESET}"
            )

        return f"{line}{_Whitespace.END_MARKER}"

    def render_line_number(self, line: str, line_number: int, *, padding: int) -> str:
        """Prefix the line with a line number, right-aligned to the specified padding."""
        if self.use_color:
            return (
                f"{_Styles.LINE_NUMBER}"
                f"{line_number:>{padding}}"
                f"{RESET}"
                f" {line}"
            )

        return f"{line_number:>{padding}} {line}"

    def render_spaces(self, line: str) -> str:
        """Replace interior spaces and trailing spaces with distinct visible markers."""
        rendered = line
        trailing_count = len(rendered) - len(rendered.rstrip(" "))

        # Remove trailing spaces before replacing them with markers.
        if trailing_count:
            rendered = rendered[:-trailing_count]

        if self.use_color:
            space_marker = f"{_Styles.SPACE_MARKER}{_Whitespace.SPACE_MARKER}{RESET}"

            rendered = rendered.replace(" ", space_marker)
            rendered = rendered + _Styles.SPACE_MARKER + (
                    _Whitespace.TRAILING_SPACE_MARKER * trailing_count) + RESET
        else:
            rendered = rendered.replace(" ", _Whitespace.SPACE_MARKER)
            rendered = rendered + (_Whitespace.TRAILING_SPACE_MARKER * trailing_count)

        return rendered

    def render_tabs(self, line: str) -> str:
        """Replace tabs with visible markers."""
        if self.use_color:
            tab_marker = (
                f"{_Styles.TAB_MARKER}"
                f"{_Whitespace.TAB_MARKER}"
                f"{RESET}"
            )

            return line.replace("\t", tab_marker)

        return line.replace("\t", _Whitespace.TAB_MARKER)

    @override
    def validate_option_ranges(self) -> None:
        """Validate that option values fall within their allowed numeric or logical ranges."""
        if self.args.max_lines < 1:
            self.print_error_and_exit("--max-lines must be >= 1")

        if self.args.start == 0:
            self.print_error_and_exit("--start cannot be 0")


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Show().run()


if __name__ == "__main__":
    raise SystemExit(main())
