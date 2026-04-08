"""Implements a program that sorts files and prints them to standard output."""

import argparse
import datetime
import random
import re
import sys
from collections.abc import Iterable
from typing import Any, Callable, Final, NoReturn, override

from dateutil.parser import ParserError, parse

from pyrcli.cli import TextProgram, text
from pyrcli.cli.ansi import ForegroundColors
from pyrcli.cli.io import InputFile

# Matches one or more consecutive characters that are not digits, commas, or periods.
_CURRENCY_SANITIZE_REGEX: Final[str] = r"[^0-9,.]+"

# Matches (and captures) one or more decimal digits.
_DIGIT_TOKEN_REGEX: Final[str] = r"(\d+)"

# Matches one or more consecutive characters that are not Unicode word characters or whitespace.
_NON_WORD_OR_WHITESPACE_REGEX: Final[str] = r"[^\w\s]+"

# Sort key segment where ``0`` indicates a parsed date and ``1`` indicates a text fallback.
type _DateSortSegment = tuple[int, datetime.datetime | str]

# Sort key segment where ``0`` indicates a numeric value and ``1`` indicates a text fallback.
type _NumericSortSegment = tuple[int, float | str]


class _Styles:
    """Namespace for ANSI styling constants."""
    COLON: Final[str] = ForegroundColors.BRIGHT_CYAN
    FILE_NAME: Final[str] = ForegroundColors.BRIGHT_MAGENTA


class Order(TextProgram):
    """Command implementation for sorting files and printing them to standard output."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="order")

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="sort and print FILES",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)
        sort_group = parser.add_mutually_exclusive_group()

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        sort_group.add_argument("-c", "--currency-sort", action="store_true", help="sort lines by currency value")
        sort_group.add_argument("-d", "--dictionary-order", action="store_true", help="sort lines in dictionary order")
        sort_group.add_argument("-D", "--date-sort", action="store_true", help="sort lines by date")
        sort_group.add_argument("-n", "--natural-sort", action="store_true",
                                help="sort lines in natural order (numbers numeric)")
        sort_group.add_argument("-R", "--random-sort", action="store_true", help="sort lines in random order")
        parser.add_argument("--decimal-comma", action="store_true",
                            help="interpret comma as the decimal separator (requires --currency-sort or --natural-sort)")
        parser.add_argument("-b", "--ignore-leading-blanks", action="store_true", help="ignore leading whitespace")
        parser.add_argument("-i", "--ignore-case", action="store_true", help="ignore case when comparing")
        parser.add_argument("-f", "--skip-fields", help="skip the first N non-empty fields when comparing (N >= 1)",
                            metavar="N", type=int)
        parser.add_argument("--field-separator",
                            help="split lines into fields using SEP (default: <space>; requires --skip-fields)",
                            metavar="SEP")
        parser.add_argument("-r", "--reverse", action="store_true", help="reverse the order of the sort")
        parser.add_argument("--no-blank", action="store_true", help="suppress all blank lines")
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
        # --field-separator is only meaningful with --skip-fields.
        if self.args.field_separator is not None and self.args.skip_fields is None:
            self.print_error_and_exit("--field-separator requires --skip-fields")

        # --decimal-comma is only meaningful with --currency-sort or --natural-sort.
        if self.args.decimal_comma and not any((self.args.currency_sort, self.args.natural_sort)):
            self.print_error_and_exit("--decimal-comma requires --currency-sort or --natural-sort")

    def generate_currency_sort_key(self, line: str) -> list[_NumericSortSegment]:
        """
        Return a sort key that orders currency-like values numerically when possible.

        - Returns a list of tuples used for comparison.
        - Each tuple is ``(0, number)`` when the text parses as a number.
        - Otherwise returns ``(1, text)`` to fall back to lexicographic comparison.
        """
        segments: list[_NumericSortSegment] = []

        for field in self.get_sort_fields(line, filter_empty_fields=True):
            negative = "-" in field or ("(" in field and ")" in field)
            number = self.normalize_number(re.sub(pattern=_CURRENCY_SANITIZE_REGEX, repl="", string=field))

            try:
                segments.append((0, float(number) * (-1 if negative else 1)))
            except ValueError:
                segments.append((1, field))

        return segments

    def generate_date_sort_key(self, line: str) -> list[_DateSortSegment]:
        """
        Return a sort key that orders date-like values chronologically when possible.

        - Returns a list of tuples used for comparison.
        - Each tuple is ``(0, date)`` when the text parses as a date.
        - Otherwise returns ``(1, text)`` to fall back to lexicographic comparison.
        """
        segments: list[_DateSortSegment] = []

        for field in self.get_sort_fields(line, filter_empty_fields=True):
            try:
                segments.append((0, parse(field)))
            except ParserError:
                segments.append((1, field))

        return segments

    def generate_default_sort_key(self, line: str) -> list[str]:
        """Return a sort key that orders lines lexicographically."""
        return self.get_sort_fields(line)

    def generate_dictionary_sort_key(self, line: str) -> list[str]:
        """Return a sort key that implements case-insensitive dictionary order while ignoring punctuation."""
        sort_fields = []

        for field in self.get_sort_fields(line):
            # Remove everything except Unicode word characters and whitespace.
            sort_fields.append(re.sub(pattern=_NON_WORD_OR_WHITESPACE_REGEX, repl="", string=field))

        return sort_fields

    def generate_natural_sort_key(self, line: str) -> list[_NumericSortSegment]:
        """
        Return a sort key that orders text lexicographically and numbers numerically when possible.

        - Returns a list of tuples used for comparison.
        - Each tuple is ``(0, number)`` when the text parses as a number.
        - Otherwise returns ``(1, text)`` to fall back to lexicographic comparison.
        """
        segments: list[_NumericSortSegment] = []

        for field in self.get_sort_fields(line, filter_empty_fields=True):
            try:
                segments.append((0, float(self.normalize_number(field))))
            except ValueError:
                # Fall back to splitting on digit boundaries for mixed alphanumeric fields.
                for chunk in re.split(pattern=_DIGIT_TOKEN_REGEX, string=field):
                    if not chunk:  # Skip empty chunks.
                        continue

                    if chunk.isdigit():
                        segments.append((0, int(chunk)))
                    else:
                        segments.append((1, chunk))

        return segments

    def get_sort_fields(self, line: str, *, filter_empty_fields: bool = False) -> list[str]:
        """Return normalized sort fields after optional empty-field filtering and applying ``--skip-fields``."""
        normalized = self.normalize_line(line)
        separator = self.args.field_separator or " "
        skip = self.args.skip_fields
        fields = text.split_csv(normalized, separator=separator, on_error=self.print_error_and_exit)

        # When skipping fields, discard empty tokens first so skip counts apply to "real" fields.
        if filter_empty_fields or skip:
            fields = [field for field in fields if field]

        if skip:
            fields = fields[skip:]

        return fields

    def get_sort_key(self) -> Callable[[str], Any]:
        """Return the sort key function for the configured sort mode."""
        if self.args.currency_sort:
            return self.generate_currency_sort_key

        if self.args.date_sort:
            return self.generate_date_sort_key

        if self.args.dictionary_order:
            return self.generate_dictionary_sort_key

        if self.args.natural_sort:
            return self.generate_natural_sort_key

        return self.generate_default_sort_key

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        lines = list(input_lines)  # Materialize to a list; sort_and_print_lines requires a list for in-place sorting.

        self.print_file_header(file_name="")
        self.sort_and_print_lines(lines)

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        self.sort_and_print_lines(sys.stdin.readlines())  # sort_and_print_lines requires a list for in-place sorting.

    def normalize_line(self, line: str) -> str:
        """Return the line with trailing whitespace removed and optional leading-blank and case normalization."""
        normalized = line.rstrip()

        if self.args.ignore_leading_blanks:
            normalized = normalized.lstrip()

        if self.args.ignore_case:
            normalized = normalized.casefold()

        return normalized

    def normalize_number(self, number: str) -> str:
        """Return the number with a period "." as the decimal separator and no thousands separators."""
        if self.args.decimal_comma:
            # Remove thousands separator, then replace commas with decimals.
            return number.replace(".", "").replace(",", ".")

        # Remove thousands separator.
        return number.replace(",", "")

    @override
    def normalize_options(self) -> None:
        """Apply derived defaults and adjust option values for consistent internal use."""
        # Dictionary order and natural sort normalize case internally.
        if self.args.dictionary_order or self.args.natural_sort:
            self.args.ignore_case = True

        # Suppress file headers when standard input is the only source.
        if not self.args.files and not self.args.stdin_files:
            self.args.no_file_name = True

    def print_file_header(self, file_name: str) -> None:
        """Print the file header for ``file_name``."""
        if self.should_print_file_header():
            print(self.format_file_header(file_name, file_name_style=_Styles.FILE_NAME, colon_style=_Styles.COLON))

    @override
    def process_input_file(self, input_file: InputFile) -> None:
        """Process the text stream from ``input_file``."""
        self.print_file_header(input_file.file_name)
        self.sort_and_print_lines(input_file.text_stream.readlines())

    def sort_and_print_lines(self, lines: list[str]) -> None:
        """Sort and print lines to standard output according to command-line options."""
        if self.args.random_sort:
            random.shuffle(lines)
        else:
            lines.sort(key=self.get_sort_key(), reverse=self.args.reverse)

        for line in text.iter_normalized_lines(lines):
            if self.args.no_blank and not line.rstrip():
                continue

            print(line)

    @override
    def validate_option_ranges(self) -> None:
        """Validate that option values fall within their allowed numeric or logical ranges."""
        if self.args.skip_fields is not None and self.args.skip_fields < 1:
            self.print_error_and_exit("--skip-fields must be >= 1")


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Order().run()


if __name__ == "__main__":
    raise SystemExit(main())
