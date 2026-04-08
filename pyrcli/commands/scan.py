"""Implements a program that prints lines matching patterns in files."""

import argparse
import sys
from collections.abc import Iterable, Sequence
from typing import Final, NamedTuple, NoReturn, override

from pyrcli.cli import CompiledPatterns, TextProgram, patterns, render, text
from pyrcli.cli.ansi import ForegroundColors, RESET
from pyrcli.cli.io import InputFile

# Exit code when no matches are found.
_NO_MATCHES_EXIT_CODE: Final[int] = 1


class _Match(NamedTuple):
    """Line number and text content of a matched line."""
    line_number: int
    line: str


class _Styles:
    """Namespace for ANSI styling constants."""
    COLON: Final[str] = ForegroundColors.BRIGHT_CYAN
    FILE_NAME: Final[str] = ForegroundColors.BRIGHT_MAGENTA
    LINE_NUMBER: Final[str] = ForegroundColors.BRIGHT_GREEN
    MATCH: Final[str] = ForegroundColors.BRIGHT_RED


class Scan(TextProgram):
    """
    Command implementation for printing lines matching patterns in files.

    Attributes:
        match_found: Whether any match was found.
        patterns: Compiled patterns to match.
    """

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="scan", error_exit_code=2)

        self.match_found: bool = False
        self.patterns: CompiledPatterns = []

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="print lines matching patterns in FILES",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)
        count_group = parser.add_mutually_exclusive_group()

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        parser.add_argument("-e", "--find", action="extend",
                            help="print lines that match PATTERN (repeat --find to require all patterns)",
                            metavar="PATTERN", nargs=1)
        parser.add_argument("-i", "--ignore-case", action="store_true", help="ignore case when matching")
        parser.add_argument("-v", "--invert-match", action="store_true", help="print lines that do not match")
        count_group.add_argument("-c", "--count", action="store_true", help="print count of matching lines per file")
        count_group.add_argument("-C", "--count-nonzero", action="store_true",
                                 help="print count of matching lines for files with a match")
        parser.add_argument("-n", "--line-number", action="store_true", help="show line number for each matching line")
        parser.add_argument("-H", "--no-file-name", action="store_true", help="suppress file name prefixes")
        parser.add_argument("-q", "--quiet", "--silent", action="store_true",
                            help="suppress normal output (matches, counts, and file names)")
        parser.add_argument("-s", "--no-messages", action="store_true", help="suppress file error messages")
        parser.add_argument("--color", choices=("on", "off"), default="on",
                            help="use color for file names, matches, and line numbers (default: on)")
        parser.add_argument("--latin1", action="store_true", help="read FILES as latin-1 (default: utf-8)")
        parser.add_argument("--stdin-files", action="store_true", help="read FILES from standard input (one per line)")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    def collect_matches(self, lines: Iterable[str]) -> list[_Match]:
        """
        Return matched lines with line numbers for the configured patterns.

        - Applies match styling when color is enabled and ``--invert-match`` is not set.
        - Raises ``SystemExit(0)`` immediately when ``--quiet`` is set and a match is found.
        """
        matches: list[_Match] = []

        for line_number, line in enumerate(text.iter_normalized_lines(lines), start=1):
            if patterns.matches_all_patterns(line, compiled_patterns=self.patterns) != self.args.invert_match:
                # Exit early if --quiet.
                if self.args.quiet:
                    raise SystemExit(0)

                self.match_found = True

                if self.use_color and not self.args.invert_match:
                    line = render.style_matches(line, patterns=self.patterns, ansi_style=_Styles.MATCH)

                matches.append(_Match(line_number, line))

        return matches

    @override
    def exit_if_errors(self) -> None:
        """Raise ``SystemExit`` if a match was not found."""
        super().exit_if_errors()

        if not self.match_found:
            raise SystemExit(_NO_MATCHES_EXIT_CODE)

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        self.print_matches(input_lines, source_file="")

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        # Printing counts requires the input to be buffered.
        if self.is_printing_counts():
            self.print_matches(sys.stdin.readlines(), source_file="")
        else:
            self.print_matches(sys.stdin, source_file="")

    @override
    def initialize_runtime_state(self) -> None:
        """
        Initialize runtime state derived from parsed options.

        - Raises ``SystemExit(1)`` if no ``--find`` patterns are provided.
        - Compiles ``--find`` patterns.
        """
        super().initialize_runtime_state()

        if not self.args.find:
            raise SystemExit(_NO_MATCHES_EXIT_CODE)

        self.patterns = patterns.compile_patterns(self.args.find, ignore_case=self.args.ignore_case,
                                                  on_error=self.print_error_and_exit)

    def is_printing_counts(self) -> bool:
        """Return ``True`` if line counts will be printed."""
        return self.args.count or self.args.count_nonzero

    @override
    def normalize_options(self) -> None:
        """Apply derived defaults and adjust option values for consistent internal use."""
        # Suppress file headers when standard input is the only source.
        if not self.args.files and not self.args.stdin_files:
            self.args.no_file_name = True

    def print_match_results(self, matches: Sequence[_Match], *, source_file: str) -> None:
        """Print match counts or matched lines according to command-line options."""
        file_name = ""

        if self.should_print_file_header():
            file_name = self.format_file_header(source_file, file_name_style=_Styles.FILE_NAME,
                                                colon_style=_Styles.COLON)

        if self.is_printing_counts():
            print(f"{file_name}{len(matches)}")
        elif matches:
            padding = len(str(matches[-1].line_number))  # Line number from the last match determines pad width.

            if file_name:
                print(file_name)

            for line_number, line in matches:
                if self.args.line_number:
                    if self.use_color:
                        print(
                            f"{_Styles.LINE_NUMBER}"
                            f"{line_number:>{padding}}"
                            f"{_Styles.COLON}:"
                            f"{RESET}",
                            end=""
                        )
                    else:
                        print(f"{line_number:>{padding}}:", end="")

                print(line)

    def print_matches(self, lines: Iterable[str], *, source_file: str) -> None:
        """Search lines and print matches or counts according to command-line options."""
        matches = self.collect_matches(lines)

        # With --count-nonzero, suppress output for inputs with zero matches.
        if self.args.count_nonzero and not matches:
            return

        self.print_match_results(matches, source_file=source_file)

    @override
    def process_input_file(self, input_file: InputFile) -> None:
        """Process the text stream from ``input_file``."""
        self.print_matches(input_file.text_stream, source_file=input_file.file_name)


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Scan().run()


if __name__ == "__main__":
    raise SystemExit(main())
