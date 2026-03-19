"""Implements a program that replaces matching text in files."""

import argparse
import re
import sys
from collections.abc import Iterable, Iterator
from typing import Final, NoReturn, override

from pyrcli.cli import TextProgram, io, patterns, text
from pyrcli.cli.ansi import ForegroundColors
from pyrcli.cli.io import InputFile


class _Styles:
    """Namespace for ANSI styling constants."""
    COLON: Final[str] = ForegroundColors.BRIGHT_CYAN
    FILE_NAME: Final[str] = ForegroundColors.BRIGHT_MAGENTA


class Subs(TextProgram):
    """
    Command implementation for replacing matching text in files.

    Attributes:
        pattern: Compiled pattern to match.
    """

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="subs")

        self.pattern: re.Pattern[str] | None = None

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="replace matching text in FILES",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        parser.add_argument("-e", "--find", action="extend", help="match PATTERN (repeat --find to match any pattern)",
                            metavar="PATTERN", nargs=1, required=True)
        parser.add_argument("-r", "--replace", help="replace matches with literal STRING", metavar="STRING",
                            required=True)
        parser.add_argument("-i", "--ignore-case", action="store_true", help="ignore case when matching")
        parser.add_argument("--max-replacements", default=sys.maxsize, help="limit replacements to N per line (N >= 1)",
                            metavar="N", type=int)
        parser.add_argument("--in-place", action="store_true",
                            help="write changes back to FILES instead of standard output (requires FILES)")
        parser.add_argument("-H", "--no-file-name", action="store_true", help="suppress file name prefixes")
        parser.add_argument("--color", choices=("on", "off"), default="on",
                            help="use color for file names (default: on)")
        parser.add_argument("--latin1", action="store_true", help="read FILES as latin-1 (default: utf-8)")
        parser.add_argument("--stdin-files", action="store_true", help="read FILES from standard input (one per line)")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    @override
    def check_option_dependencies(self) -> None:
        """Enforce relationships and mutual constraints between command-line options."""
        # --in-place is only meaningful with FILES.
        if self.args.in_place and not self.args.files and not self.args.stdin_files:
            self.print_error_and_exit("--in-place requires FILES")

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        self.print_file_header(file_name="")
        self.print_replaced_lines(input_lines)

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        self.print_replaced_lines(sys.stdin)

    @override
    def initialize_runtime_state(self) -> None:
        """Initialize runtime state derived from parsed options."""
        super().initialize_runtime_state()

        # Compile search patterns into a single OR-pattern.
        if compiled := patterns.compile_patterns(self.args.find, ignore_case=self.args.ignore_case,
                                                 on_error=self.print_error_and_exit):
            self.pattern = patterns.compile_or_pattern(compiled, ignore_case=self.args.ignore_case)

    def iter_replaced_lines(self, lines: Iterable[str]) -> Iterator[str]:
        """
        Yield lines with matches replaced.

        - Yields lines unchanged when no pattern is compiled.
        """
        # Check pattern once rather than per line.
        if self.pattern:
            for line in text.iter_normalized_lines(lines):
                yield self.pattern.sub(repl=self.args.replace, string=line, count=self.args.max_replacements)
        else:
            for line in text.iter_normalized_lines(lines):
                yield line

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

    def print_replaced_lines(self, lines: Iterable[str]) -> None:
        """Print lines with pattern matches replaced."""
        for line in self.iter_replaced_lines(lines):
            print(line)

    @override
    def process_text_stream(self, input_file: InputFile) -> None:
        """Process the text stream from ``input_file``."""
        if self.args.in_place:
            # Buffer before writing to avoid reading and writing the same file simultaneously.
            lines = input_file.text_stream.readlines()

            io.write_text_file(input_file.file_name, lines=self.iter_replaced_lines(lines), encoding=self.encoding,
                               on_error=self.print_error)
        else:
            self.print_file_header(input_file.file_name)
            self.print_replaced_lines(input_file.text_stream.readlines())

    @override
    def validate_option_ranges(self) -> None:
        """Validate that option values fall within their allowed numeric or logical ranges."""
        if self.args.max_replacements < 1:
            self.print_error_and_exit("--max-replacements must be >= 1")


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Subs().run()


if __name__ == "__main__":
    raise SystemExit(main())
