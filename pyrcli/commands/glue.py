"""Implements a program that concatenates files and standard input to standard output."""

import argparse
import sys
from collections.abc import Iterable
from typing import Final, NoReturn, override

from pyrcli.cli import TextProgram, text
from pyrcli.cli.ansi import ForegroundColors, RESET
from pyrcli.cli.io import InputFile


class _Styles:
    """Namespace for ANSI styling constants."""
    END_MARKER: Final[str] = ForegroundColors.BRIGHT_BLUE
    NUMBER: Final[str] = ForegroundColors.BRIGHT_GREEN
    TAB_MARKER: Final[str] = ForegroundColors.BRIGHT_CYAN


class _Whitespace:
    """Namespace for whitespace replacement constants."""
    END_MARKER: Final[str] = "$"
    TAB_MARKER: Final[str] = ">···"


class Glue(TextProgram):
    """
    Command implementation for concatenating files and standard input to standard output.

    Attributes:
        line_number: Line number to be printed with output lines.
    """

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="glue")

        self.line_number: int = 0

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="concatenate FILES to standard output",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)
        blank_group = parser.add_mutually_exclusive_group()
        number_group = parser.add_mutually_exclusive_group()

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        number_group.add_argument("-b", "--number-nonblank", action="store_true", help="number nonblank lines")
        number_group.add_argument("-n", "--number", action="store_true", help="number lines")
        parser.add_argument("--number-width", default=6, help="pad line numbers to width N (default: 6; N >= 1)",
                            metavar="N", type=int)
        blank_group.add_argument("-s", "--squeeze-blank", action="store_true", help="suppress repeated blank lines")
        blank_group.add_argument("--no-blank", action="store_true", help="suppress blank lines")
        parser.add_argument("-E", "--show-ends", action="store_true",
                            help=f"display '{_Whitespace.END_MARKER}' at end of each line")
        parser.add_argument("-T", "--show-tabs", action="store_true",
                            help=f"display tab characters as '{_Whitespace.TAB_MARKER}'")
        parser.add_argument("--color", choices=("on", "off"), default="on",
                            help="use color for numbers and whitespace (default: on)")
        parser.add_argument("--latin1", action="store_true", help="read FILES as latin-1 (default: utf-8)")
        parser.add_argument("--stdin-files", action="store_true", help="read FILES from standard input (one per line)")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        self.print_lines(input_lines)

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        self.print_lines(sys.stdin)

    def print_lines(self, lines: Iterable[str]) -> None:
        """Print lines to standard output, applying numbering, whitespace rendering, and blank-line handling."""
        blank_line_count = 0
        numbering_enabled = self.args.number or self.args.number_nonblank

        for line in text.iter_normalized_lines(lines):
            print_number = numbering_enabled

            if not line:
                blank_line_count += 1

                if self.should_suppress_blank_line(blank_line_count):
                    continue

                if self.args.number_nonblank:
                    print_number = False
            else:
                blank_line_count = 0

            line = self.render_whitespace(line)

            if print_number:
                self.line_number += 1
                line = self.render_number(line)

            print(line)

    @override
    def process_input_file(self, input_file: InputFile) -> None:
        """Process the text stream from ``input_file``."""
        self.print_lines(input_file.text_stream)

    def render_number(self, line: str) -> str:
        """Prefix a formatted line number to the line."""
        if self.use_color:
            return (
                f"{_Styles.NUMBER}"
                f"{self.line_number:>{self.args.number_width}}"
                f"{RESET}"
                f" {line}"
            )

        return f"{self.line_number:>{self.args.number_width}} {line}"

    def render_whitespace(self, line: str) -> str:
        """Render visible representations of tabs and end-of-line markers."""
        rendered = line

        # Replace tabs before appending the end marker to preserve correct ordering.
        if self.args.show_tabs:
            if self.use_color:
                tab_marker = (
                    f"{_Styles.TAB_MARKER}"
                    f"{_Whitespace.TAB_MARKER}"
                    f"{RESET}"
                )

                rendered = rendered.replace("\t", tab_marker)
            else:
                rendered = rendered.replace("\t", _Whitespace.TAB_MARKER)

        if self.args.show_ends:
            if self.use_color:
                rendered = (
                    f"{rendered}"
                    f"{_Styles.END_MARKER}"
                    f"{_Whitespace.END_MARKER}"
                    f"{RESET}"
                )
            else:
                rendered = rendered + _Whitespace.END_MARKER

        return rendered

    def should_suppress_blank_line(self, blank_line_count: int) -> bool:
        """Return ``True`` if a blank line should be suppressed."""
        return self.args.no_blank or (self.args.squeeze_blank and blank_line_count > 1)

    @override
    def validate_option_ranges(self) -> None:
        """Validate that option values fall within their allowed numeric or logical ranges."""
        if self.args.number_width < 1:
            self.print_error_and_exit("--number-width must be >= 1")


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Glue().run()


if __name__ == "__main__":
    raise SystemExit(main())
