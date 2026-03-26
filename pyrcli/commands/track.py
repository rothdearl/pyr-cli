"""Implements a program that prints the last part of files, optionally following new lines."""

import argparse
import sys
import time
from collections.abc import Collection, Iterable
from threading import Thread
from typing import Final, NoReturn, override

from pyrcli.cli import TextProgram, text
from pyrcli.cli.ansi import ForegroundColors
from pyrcli.cli.io import InputFile

# Interval in seconds between file content polls when following.
_POLLING_INTERVAL: Final[float] = 0.5


class _Styles:
    """Namespace for ANSI styling constants."""
    COLON: Final[str] = ForegroundColors.BRIGHT_CYAN
    FILE_NAME: Final[str] = ForegroundColors.BRIGHT_MAGENTA


class Track(TextProgram):
    """Command implementation for printing the last part of files, optionally following new lines."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="track")

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False,
                                         description="print the last part of FILES, optionally following new lines",
                                         epilog="read from standard input when no FILES are specified", prog=self.name)

        parser.add_argument("files", help="read from FILES", metavar="FILES", nargs="*")
        parser.add_argument("-n", "--lines", default=10,
                            help="print the last N lines, or all but the first N if N < 0 (default: 10)", metavar="N",
                            type=int)
        parser.add_argument("-f", "--follow", action="store_true", help="output appended lines as the file grows")
        parser.add_argument("-H", "--no-file-name", action="store_true", help="suppress file name prefixes")
        parser.add_argument("--color", choices=("on", "off"), default="on",
                            help="use color for file names (default: on)")
        parser.add_argument("--latin1", action="store_true", help="read FILES as latin-1 (default: utf-8)")
        parser.add_argument("--stdin-files", action="store_true", help="read FILES from standard input (one per line)")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    @override
    def post_execute(self, processed_files: Collection[str]) -> None:
        """Run post-execution logic after all input has been processed."""
        file_count = len(processed_files)

        if self.args.follow and processed_files:
            for thread in self.start_following_threads(processed_files, print_file_name_on_update=file_count > 1):
                thread.join()

    def follow_file(self, file_name: str, print_file_name_on_update: bool) -> None:
        """
        Continuously poll ``file_name`` and print lines appended since the previous read.

        - The entire file is re-read on each poll; only newly appended lines are printed.
        """
        try:
            # Get the initial file content.
            with open(file_name, mode="rt", encoding=self.encoding) as f:
                previous_content = f.read()

            # Follow file until Ctrl-C.
            while True:
                # Re-open the file with each iteration and check for changes.
                with open(file_name, mode="rt", encoding=self.encoding) as f:
                    next_content = f.read()

                    if previous_content != next_content:
                        print_index = 0

                        if next_content.startswith(previous_content):
                            print_index = len(previous_content)
                        elif len(next_content) < len(previous_content):
                            print(f"data removed in: {file_name!r}")
                        else:
                            print(f"data modified in: {file_name!r}")

                        if print_file_name_on_update:
                            self.print_file_header(file_name)

                        print(next_content[print_index:])
                        previous_content = next_content

                time.sleep(_POLLING_INTERVAL)
        except FileNotFoundError:
            self.print_error(f"{file_name!r} has been deleted")
        except (UnicodeDecodeError, OSError):
            self.print_error(f"{file_name!r} is no longer accessible")

    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None:
        """Process input received from redirected standard input."""
        lines = list(input_lines)  # Materialize to a list; print_lines requires a Sequence to compute line start.

        self.print_file_header(file_name="")
        self.print_lines(lines)

    @override
    def handle_terminal_input(self) -> None:
        """Read and process input interactively from the terminal."""
        while True:
            self.print_lines(sys.stdin.readlines())  # print_lines requires a Sequence to compute line start.

            # --follow on standard input is an infinite loop until Ctrl-C.
            if not self.args.follow:
                return

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

    def print_lines(self, lines: Collection[str]) -> None:
        """Print lines to standard output."""
        # Negative --lines: skip the first N lines.
        if self.args.lines < 0:
            start_index = abs(self.args.lines)
        else:
            # Positive --lines: print the last N lines.
            start_index = len(lines) - self.args.lines

        for index, line in enumerate(text.iter_normalized_lines(lines), start=1):
            if index > start_index:
                print(line)

    @override
    def process_input_file(self, input_file: InputFile) -> None:
        """Process the text stream from ``input_file``."""
        self.print_file_header(input_file.file_name)
        self.print_lines(input_file.text_stream.readlines())

    def start_following_threads(self, files: Iterable[str], *, print_file_name_on_update: bool) -> list[Thread]:
        """Start a thread for each file and return the started ``Thread`` objects."""
        threads = []

        for file_name in files:
            thread = Thread(target=self.follow_file, args=(file_name, print_file_name_on_update),
                            name=f"following-{file_name!r}")
            thread.start()
            threads.append(thread)

        return threads


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Track().run()


if __name__ == "__main__":
    raise SystemExit(main())
