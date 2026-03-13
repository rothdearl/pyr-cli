"""Implements a program that counts lines, words, and characters in files."""

import argparse
import re
import sys
from collections.abc import Iterable, Sequence
from typing import Final, NamedTuple, NoReturn, override

from pyrcli.cli import TextProgram, text
from pyrcli.cli.ansi import ForegroundColors, RESET
from pyrcli.cli.io import InputFile

# Matches sequences of word characters bounded by word boundaries.
_WORD_PATTERN: Final[re.Pattern[str]] = re.compile(r"\b\w+\b")


class _Counts(NamedTuple):
    """Line, word, character, and maximum line length counts."""
    lines: int
    words: int
    characters: int
    max_line_length: int


class _Styles:
    """Namespace for ANSI styling constants."""
    COUNT: Final[str] = ForegroundColors.BRIGHT_CYAN
    COUNT_TOTAL: Final[str] = ForegroundColors.BRIGHT_YELLOW
    FILE_NAME: Final[str] = ForegroundColors.BRIGHT_MAGENTA


class Tally(TextProgram):
    """
    Command implementation for counting lines, words, and characters in files.

    Attributes:
        flags: Flags for determining if a count attribute will be printed.
        received_stdin: Whether input was received from redirected standard input.
        totals: Total counts across all files.
    """

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="tally", buffer_stdin=True)

        self.flags: list[bool] = [False, False, False, False]  # [lines, words, characters, max_line_length]
        self.received_stdin: bool = False
        self.totals: _Counts = _Counts(0, 0, 0, 0)

    def accumulate_counts(self, counts: _Counts) -> None:
        """Accumulate ``counts`` into the running totals, taking the maximum for line length."""
        self.totals = _Counts(
            self.totals.lines + counts.lines,
            self.totals.words + counts.words,
            self.totals.characters + counts.characters,
            max(self.totals.max_line_length, counts.max_line_length)
        )

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False,
                                         description="count lines, words, and characters in FILES",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        parser.add_argument("-l", "--lines", action="store_true", help="print line counts")
        parser.add_argument("-c", "--chars", action="store_true", help="print character counts")
        parser.add_argument("-w", "--words", action="store_true", help="print word counts")
        parser.add_argument("-L", "--max-line-length", action="store_true", help="print maximum line length")
        parser.add_argument("--total", choices=("auto", "on", "off"), default="auto",
                            help="print total counts in an extra line (default: auto)")
        parser.add_argument("-t", "--tab-width", default=8,
                            help="use N spaces per tab when computing line length (default: 8; N >= 1)", metavar="N",
                            type=int)
        parser.add_argument("--count-width", default=8, help="pad counts to width N (default: 8; N >= 1)", metavar="N",
                            type=int)
        parser.add_argument("--color", choices=("on", "off"), default="on",
                            help="use color for counts and file names (default: on)")
        parser.add_argument("--latin1", action="store_true", help="read FILES as latin-1 (default: utf-8)")
        parser.add_argument("--stdin-files", action="store_true", help="read FILES from standard input (one per line)")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    def calculate_counts(self, lines: Iterable[str]) -> _Counts:
        """Return line, word, character, and maximum display width counts for ``lines``."""
        line_count, word_count, character_count, max_line_length = 0, 0, 0, 0

        for raw_line in lines:
            display_line = text.strip_trailing_newline(raw_line)
            max_display_width = len(display_line.expandtabs(self.args.tab_width))

            character_count += len(raw_line)
            line_count += 1
            max_line_length = max(max_display_width, max_line_length)
            word_count += len(_WORD_PATTERN.findall(display_line))

        return _Counts(line_count, word_count, character_count, max_line_length)

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        counts = self.calculate_counts(input_lines)

        self.accumulate_counts(counts)
        self.print_counts(counts, source_file="(standard input)" if self.args.files else "", is_total=False)
        self.received_stdin = True

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        counts = self.calculate_counts(sys.stdin)

        self.accumulate_counts(counts)
        self.print_counts(counts, source_file="", is_total=False)

    @override
    def initialize_runtime_state(self) -> None:
        """
        Initialize internal state derived from parsed options.

        - Defaults count flags to lines, words, and characters if none are provided.
        """
        super().initialize_runtime_state()

        for index, flag in enumerate((self.args.lines, self.args.words, self.args.chars, self.args.max_line_length)):
            if flag:
                self.flags[index] = True

        if not any(self.flags):
            for index in (0, 1, 2):
                self.flags[index] = True

    @override
    def post_execute(self, processed_files: Sequence[str]) -> None:
        """Run post-execution logic after all input has been processed."""
        file_count = len(processed_files) + 1 if self.received_stdin else 0

        if self.args.total == "on" or (self.args.total == "auto" and file_count > 1):
            self.print_counts(self.totals, source_file="total", is_total=True)

    def print_counts(self, counts: _Counts, *, source_file: str, is_total: bool) -> None:
        """Print counts for a file, applying total styling when ``is_total`` is ``True``."""
        count_color = _Styles.COUNT_TOTAL if is_total else _Styles.COUNT
        source_file_color = _Styles.COUNT_TOTAL if is_total else _Styles.FILE_NAME
        padding = self.args.count_width

        # Omit padding when only one count is printed with no file name.
        if sum(self.flags) == 1 and not source_file:
            padding = 0

        # _Counts is iterable in field order.
        for index, count in enumerate(counts):
            if self.flags[index]:
                if self.print_color:
                    print(
                        f"{count_color}"
                        f"{count:>{padding},}"
                        f"{RESET}",
                        end=""
                    )
                else:
                    print(f"{count:>{padding},}", end="")

        if source_file:
            if self.print_color:
                print(f" {source_file_color}{source_file}{RESET}")
            else:
                print(f" {source_file}")
        else:
            print()

    @override
    def process_text_stream(self, input_file: InputFile) -> None:
        """Process the text stream for a single input file."""
        counts = self.calculate_counts(input_file.text_stream)

        self.accumulate_counts(counts)
        self.print_counts(counts, source_file=input_file.file_name, is_total=False)

    @override
    def validate_option_ranges(self) -> None:
        """Validate that option values fall within their allowed numeric or logical ranges."""
        if self.args.count_width < 1:
            self.print_error_and_exit("--count-width must be >= 1")

        if self.args.tab_width < 1:
            self.print_error_and_exit("--tab-width must be >= 1")


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Tally().run()


if __name__ == "__main__":
    raise SystemExit(main())
