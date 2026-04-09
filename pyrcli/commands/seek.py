"""Implements a program that searches for files in a directory hierarchy."""

import argparse
import os
import sys
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Final, NoReturn, override

from pyrcli.cli import CLIProgram, CompiledPatterns, io, patterns, render, terminal, text
from pyrcli.cli.ansi import ForegroundColors

# Exit code when no matches are found.
_NO_MATCHES_EXIT_CODE: Final[int] = 1


class _Styles:
    """Namespace for ANSI styling constants."""
    MATCH: Final[str] = ForegroundColors.BRIGHT_RED


class Seek(CLIProgram):
    """Command implementation for searching for files in a directory hierarchy.

    Attributes:
        match_found: Whether any match was found.
        mtime_threshold: Modification time threshold in seconds (``None`` when no ``--mtime-*`` option is set).
        name_patterns: Compiled name patterns to match.
        path_patterns: Compiled path patterns to match.
    """

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="seek", error_exit_code=2)

        self.match_found: bool = False
        self.mtime_threshold: int | None = None
        self.name_patterns: CompiledPatterns = []
        self.path_patterns: CompiledPatterns = []

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False, description="search for files in a directory hierarchy",
                                         epilog="search the current directory when no DIRECTORIES are specified",
                                         prog=self.name)
        modified_group = parser.add_mutually_exclusive_group()

        parser.add_argument("directories", help="search starting points", metavar="DIRECTORIES", nargs="*")
        parser.add_argument("-n", "--name", action="extend",
                            help="print files whose names match PATTERN (repeat --name to require all patterns)",
                            metavar="PATTERN", nargs=1)
        parser.add_argument("-p", "--path", action="extend",
                            help="print files whose paths match PATTERN (repeat --path to require all patterns)",
                            metavar="PATTERN", nargs=1)
        parser.add_argument("-i", "--ignore-case", action="store_true", help="ignore case when matching")
        parser.add_argument("-v", "--invert-match", action="store_true", help="print files that do not match")
        parser.add_argument("--type", choices=("d", "f"), help="print only directories (d) or regular files (f)")
        parser.add_argument("--empty-only", action="store_true", help="print only empty files")
        modified_group.add_argument("--mtime-days",
                                    help="print files by modification time (+N: older than N days; -N: within last N days)",
                                    metavar="N", type=int)
        modified_group.add_argument("--mtime-hours",
                                    help="print files by modification time (+N: older than N hours; -N: within last N hours)",
                                    metavar="N", type=int)
        modified_group.add_argument("--mtime-mins",
                                    help="print files by modification time (+N: older than N minutes; -N: within last N minutes)",
                                    metavar="N", type=int)
        parser.add_argument("--max-depth", default=sys.maxsize,
                            help="descend at most N levels below the starting points (N >= 1)", metavar="N", type=int)
        parser.add_argument("--abs", action="store_true", help="print absolute paths")
        parser.add_argument("--dot-prefix", action="store_true",
                            help="prefix relative paths with './' (print '.' for current directory)")
        parser.add_argument("--quotes", action="store_true", help="print file paths in double quotes")
        parser.add_argument("-q", "--quiet", "--silent", action="store_true", help="suppress normal output")
        parser.add_argument("-s", "--no-messages", action="store_true", help="suppress file error messages")
        parser.add_argument("--color", choices=("on", "off"), default="on", help="use color for matches (default: on)")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    def check_path_filters(self, path: Path) -> bool:
        """Return ``True`` if the path matches all enabled filters.

        - Calls ``print_error()`` and returns ``False`` on ``PermissionError``.
        """
        try:
            if self.args.type:
                is_dir = path.is_dir()

                if self.args.type == "d" and not is_dir:
                    return False

                if self.args.type == "f" and is_dir:
                    return False

            if self.args.empty_only:
                if path.is_dir():
                    if os.listdir(path):
                        return False
                else:
                    if path.lstat().st_size:
                        return False

            if self.mtime_threshold is not None:
                age_seconds = time.time() - path.lstat().st_mtime

                if self.mtime_threshold < 0:
                    return age_seconds < abs(self.mtime_threshold)

                return age_seconds > self.mtime_threshold
        except PermissionError:
            self.print_error(f"{path!r}: permission denied")
            return False

        # All active filters passed.
        return True

    @override
    def execute(self) -> None:
        """Execute the command using the prepared runtime state."""
        if terminal.stdin_is_redirected():
            self.print_paths(io.iter_stdin_lines())

            # Process any additional directories.
            if self.args.directories:
                self.print_paths(self.args.directories)
        else:
            self.print_paths(self.args.directories or [os.curdir])

    @override
    def exit_if_errors(self) -> None:
        """Raise ``SystemExit`` if a match was not found."""
        super().exit_if_errors()

        if not self.match_found:
            raise SystemExit(_NO_MATCHES_EXIT_CODE)

    @override
    def initialize_runtime_state(self) -> None:
        """Initialize runtime state derived from parsed options.

        - Converts any provided ``--mtime-*`` option to ``mtime_threshold`` in seconds.
        - Compiles ``--name`` and ``--path`` patterns when provided.
        """
        super().initialize_runtime_state()

        # --mtime options are mutually exclusive; only one may be provided.
        if self.args.mtime_days or self.args.mtime_hours or self.args.mtime_mins:
            if self.args.mtime_days is not None:
                self.mtime_threshold = self.args.mtime_days * 86400
            elif self.args.mtime_hours is not None:
                self.mtime_threshold = self.args.mtime_hours * 3600
            else:
                self.mtime_threshold = self.args.mtime_mins * 60

        if self.args.name:
            self.name_patterns = patterns.compile_patterns(self.args.name, ignore_case=self.args.ignore_case,
                                                           on_error=self.print_error_and_exit)

        if self.args.path:
            self.path_patterns = patterns.compile_patterns(self.args.path, ignore_case=self.args.ignore_case,
                                                           on_error=self.print_error_and_exit)

    def path_matches_patterns(self, name_part: str, path_part: str) -> bool:
        """Return ``True`` if the ``name_part`` and ``path_part`` match all provided name and path patterns."""
        if not patterns.matches_all_patterns(name_part, compiled_patterns=self.name_patterns):
            return False

        if not patterns.matches_all_patterns(path_part, compiled_patterns=self.path_patterns):
            return False

        return True

    def print_path(self, path: Path) -> None:
        """Print the path if it matches the specified search criteria.

        - Sets ``match_found`` to ``True`` when a match is printed.
        - Raises ``SystemExit(0)`` when ``--quiet`` is set and a match is found.
        """
        is_current_directory = path.name == ""
        name_part = path.name or os.curdir  # The current directory has no name component.
        path_part = str(path.parent) if len(path.parts) > 1 else ""  # Do not include '.' in the path part.

        # Skip the current directory unless --dot-prefix is set.
        if is_current_directory and not self.args.dot_prefix:
            return

        matches = self.path_matches_patterns(name_part, path_part) and self.check_path_filters(path)

        if matches == self.args.invert_match:
            return

        # Exit early if --quiet.
        if self.args.quiet:
            raise SystemExit(0)

        self.match_found = True

        if self.use_color and not self.args.invert_match:
            name_part = render.style_matches(name_part, patterns=self.name_patterns, ansi_style=_Styles.MATCH)
            path_part = render.style_matches(path_part, patterns=self.path_patterns, ansi_style=_Styles.MATCH)

        if self.args.abs:
            # Do not join the current working directory with '.'.
            if is_current_directory:
                display_path = os.path.join(Path.cwd(), path_part)
            else:
                display_path = os.path.join(Path.cwd(), path_part, name_part)
        else:
            # Do not join the current directory with '.'.
            if self.args.dot_prefix and not is_current_directory:
                display_path = os.path.join(os.curdir, path_part, name_part)
            else:
                display_path = os.path.join(path_part, name_part)

        if self.args.quotes:
            display_path = f'"{display_path}"'

        print(display_path)

    def print_paths(self, directories: Iterable[str]) -> None:
        """Traverse starting directories up to ``--max-depth`` and print matching paths.

        - Calls ``print_error()`` for missing or inaccessible directories; processing continues with the next directory.
        """
        for directory in text.iter_normalized_lines(directories):
            if os.path.exists(directory):
                root = Path(directory)

                self.print_path(root)

                try:
                    for path in io.iter_descendant_paths(root, max_depth=self.args.max_depth):
                        self.print_path(path)
                except PermissionError as error:
                    self.print_error(f"{error.filename!r}: permission denied")
            else:
                self.print_error(f"{directory!r}: no such file or directory")

    @override
    def validate_option_ranges(self) -> None:
        """Validate that option values fall within their allowed numeric or logical ranges."""
        if self.args.max_depth < 1:
            self.print_error_and_exit("--max-depth must be >= 1")


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return Seek().run()


if __name__ == "__main__":
    raise SystemExit(main())
