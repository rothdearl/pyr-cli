"""Implements a program that filters duplicate or unique lines from files."""

import argparse
import sys
from collections.abc import Iterable, Sequence
from typing import Final, NoReturn, override

from pyrcli.cli import TextProgram, ansi, io, text


class _Styles:
    """Namespace for ANSI styling constants."""
    COLON: Final[str] = ansi.ForegroundColors.BRIGHT_CYAN
    FILE_NAME: Final[str] = ansi.ForegroundColors.BRIGHT_MAGENTA
    GROUP_COUNT: Final[str] = ansi.ForegroundColors.BRIGHT_GREEN


class Dupe(TextProgram):
    """Command implementation for filtering duplicate or unique lines from files."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="dupe", buffer_stdin=True)

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Build and return an argument parser."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="find and filter duplicate lines in FILES",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)
        print_group = parser.add_mutually_exclusive_group()

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        print_group.add_argument("-d", "--repeated", action="store_true", help="print one duplicate line per group")
        print_group.add_argument("-D", "--all-repeated", action="store_true",
                                 help="print all duplicate lines per group")
        print_group.add_argument("-g", "--group", action="store_true",
                                 help="print all lines, grouping identical lines and separating groups with an empty line")
        print_group.add_argument("-u", "--unique", action="store_true", help="print unique lines only")
        parser.add_argument("-c", "--count", action="store_true", help="prefix lines with the number of occurrences")
        parser.add_argument("--count-width", default=4, help="pad occurrence counts to width N (default: 4; N >= 1)",
                            metavar="N", type=int)
        parser.add_argument("-H", "--no-file-name", action="store_true", help="suppress file name prefixes")
        parser.add_argument("-a", "--adjacent", action="store_true",
                            help="compare adjacent lines only (do not search entire file)")
        parser.add_argument("-i", "--ignore-case", action="store_true", help="ignore case when comparing")
        parser.add_argument("--ignore-blank", action="store_true", help="ignore blank lines")
        parser.add_argument("-f", "--skip-fields", help="skip the first N non-empty fields when comparing (N >= 1)",
                            metavar="N", type=int)
        parser.add_argument("--field-separator",
                            help="split lines into fields using SEP (default: <space>; requires --skip-fields)",
                            metavar="SEP")
        parser.add_argument("-s", "--skip-chars", help="skip the first N characters when comparing (N >= 0)",
                            metavar="N", type=int)
        parser.add_argument("-m", "--max-chars", help="compare at most N characters (N >= 1)", metavar="N", type=int)
        parser.add_argument("-w", "--skip-whitespace", action="store_true",
                            help="ignore leading and trailing whitespace when comparing")
        parser.add_argument("--color", choices=("on", "off"), default="on",
                            help="use color for file names and counts (default: on)")
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

    def get_compare_key(self, line: str) -> str:
        """Return a normalized comparison key derived from the line, applying skip, trim, and case options."""
        compare_key = line

        if self.args.skip_whitespace:
            compare_key = compare_key.strip()

        if self.args.skip_fields:
            separator = self.args.field_separator or " "

            compare_key = text.split_csv(compare_key, separator=separator, on_error=self.print_error_and_exit)
            compare_key = separator.join(compare_key[self.args.skip_fields:])

        if self.args.max_chars or self.args.skip_chars:
            start_index = self.args.skip_chars or 0
            end_index = start_index + self.args.max_chars if self.args.max_chars else len(line)

            compare_key = compare_key[start_index:end_index]

        if self.args.ignore_case:
            compare_key = compare_key.casefold()

        return compare_key

    def group_adjacent_matching_lines(self, lines: Iterable[str]) -> list[list[str]]:
        """Return groups of adjacent lines that share the same comparison key, preserving input order."""
        groups = []
        previous_key = None

        for line in text.iter_normalized_lines(lines):
            next_key = self.get_compare_key(line)

            if not self.should_include_key(next_key):
                continue

            if next_key != previous_key:
                groups.append([])

            groups[-1].append(line)  # Always append to the last group.
            previous_key = next_key

        return groups

    def group_and_print_lines(self, lines: Iterable[str]) -> None:
        """Group lines by the configured strategy and print the resulting groups."""
        if self.args.adjacent:
            line_groups = self.group_adjacent_matching_lines(lines)
        else:
            line_groups = self.group_lines_by_key(lines).values()

        self.print_line_groups(line_groups)

    def group_lines_by_key(self, lines: Iterable[str]) -> dict[str, list[str]]:
        """Return a mapping from comparison keys to grouped lines."""
        group_map = {}

        for line in text.iter_normalized_lines(lines):
            key = self.get_compare_key(line)

            if not self.should_include_key(key):
                continue

            if key in group_map:
                group_map[key].append(line)
            else:
                group_map[key] = [line]

        return group_map

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        self.print_file_header(file_name="")
        self.group_and_print_lines(input_lines)

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        self.group_and_print_lines(sys.stdin)

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

    def print_line_groups(self, line_groups: Iterable[Sequence[str]]) -> None:
        """Print line groups as duplicates, unique lines, or grouped output."""
        printed_line_count = 0

        for line_group in line_groups:
            group_count = len(line_group)

            if not self.should_print_group(group_count):
                continue

            if self.args.group and printed_line_count:
                print()

            for line_index, line in enumerate(line_group):
                group_count_str = ""

                if self.args.count:
                    # Only print the group count for the first line.
                    if line_index == 0:
                        if self.print_color:
                            group_count_str = (
                                f"{_Styles.GROUP_COUNT}"
                                f"{group_count:>{self.args.count_width},}"
                                f"{_Styles.COLON}:"
                                f"{ansi.RESET}"
                            )
                        else:
                            group_count_str = f"{group_count:>{self.args.count_width},}:"
                    else:
                        group_count_str = f"{' ':>{self.args.count_width}} "  # Ensure lines align.

                print(f"{group_count_str}{line}")
                printed_line_count += 1

                if not self.should_print_all_group_lines():
                    break

    @override
    def process_text_stream(self, input_file: io.InputFile) -> None:
        """Process the text stream for a single input file."""
        self.print_file_header(input_file.file_name)
        self.group_and_print_lines(input_file.text_stream)

    def should_include_key(self, key: str) -> bool:
        """Return ``True`` if ``key`` should participate in grouping."""
        return not self.args.ignore_blank or key.strip()

    def should_print_all_group_lines(self) -> bool:
        """Return ``True`` if all lines in a group should be printed."""
        return self.args.all_repeated or self.args.group

    def should_print_group(self, group_count: int) -> bool:
        """Return ``True`` if a line group should produce output."""
        if self.args.repeated or self.args.all_repeated:
            return group_count > 1

        if self.args.unique:
            return group_count == 1

        return True

    @override
    def validate_option_ranges(self) -> None:
        """Validate that option values fall within their allowed numeric or logical ranges."""
        if self.args.count_width < 1:
            self.print_error_and_exit("--count-width must be >= 1")

        if self.args.max_chars is not None and self.args.max_chars < 1:
            self.print_error_and_exit("--max-chars must be >= 1")

        if self.args.skip_chars is not None and self.args.skip_chars < 0:
            self.print_error_and_exit("--skip-chars must be >= 0")

        if self.args.skip_fields is not None and self.args.skip_fields < 1:
            self.print_error_and_exit("--skip-fields must be >= 1")


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Dupe().run_program()


if __name__ == "__main__":
    raise SystemExit(main())
