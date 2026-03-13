"""Implements a program that displays a calendar with optional date and time."""

import argparse
import calendar
import datetime
from typing import Final, NamedTuple, NoReturn, override

from pyrcli.cli import CLIProgram, render
from pyrcli.cli.platform import IS_POSIX

# Default format for printing the date and time.
_DEFAULT_DATETIME_FORMAT: Final[str] = "%a %b %-d %-I:%M%p" if IS_POSIX else "%a %b %d %I:%M%p"


class _CalendarQuarterColumnBounds(NamedTuple):
    """Character column bounds for a month within a three-month quarter row."""
    start: int
    end: int


class When(CLIProgram):
    """Command implementation for displaying a calendar with optional date and time."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        super().__init__(name="when")

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        parser = argparse.ArgumentParser(allow_abbrev=False,
                                         description="display a calendar with optional date and time",
                                         epilog="datetime format is interpreted using strftime(3)", prog=self.name)

        parser.add_argument("-c", "--calendar", choices=("m", "q", "y"), default="m",
                            help="print calendar as a month, quarter, or year (default: m)")
        parser.add_argument("-w", "--week-start", choices=("mon", "sun"), default="mon",
                            help="use monday or sunday as first day of the week (default: mon)")
        parser.add_argument("-d", "--datetime", action="store_true", help="print current date and time after calendar")
        parser.add_argument("--datetime-format", help="use STRING as datetime format (requires --datetime)",
                            metavar="STRING")
        parser.add_argument("--version", action="version", version=f"%(prog)s {self.version}")

        return parser

    @override
    def check_option_dependencies(self) -> None:
        """Enforce relationships and mutual constraints between command-line options."""
        # --datetime-format is only meaningful with --datetime.
        if self.args.datetime_format is not None and not self.args.datetime:
            self.print_error_and_exit("--datetime-format requires --datetime")

    @override
    def execute(self) -> None:
        """Execute the command using the prepared runtime state."""
        text_calendar = calendar.TextCalendar(calendar.SUNDAY if self.args.week_start == "sun" else calendar.MONDAY)

        match self.args.calendar:
            case "m":
                self.print_month(text_calendar)
            case "q":
                self.print_quarter(text_calendar)
            case _:
                self.print_year(text_calendar)

        if self.args.datetime:
            date_format = self.args.datetime_format or _DEFAULT_DATETIME_FORMAT
            now = datetime.datetime.now()

            try:
                print()
                print(now.strftime(date_format))
            except ValueError:  # Raised for invalid format directives on Windows; unreachable on POSIX.
                self.print_error_and_exit("invalid datetime format")

    @staticmethod
    def get_quarter_column_bounds_for_month(month: int) -> _CalendarQuarterColumnBounds:
        """Return the character column bounds for ``month`` within a three-month quarter row."""
        bounds_by_index = (
            _CalendarQuarterColumnBounds(0, 20),
            _CalendarQuarterColumnBounds(26, 46),
            _CalendarQuarterColumnBounds(52, 72)
        )

        return bounds_by_index[(month - 1) % 3]

    @staticmethod
    def highlight(text: str) -> str:
        """Return text rendered with reverse video."""
        return render.reverse_video(text)

    def highlight_day_within_bounds(self, line: str, day: str, bounds: _CalendarQuarterColumnBounds) -> str:
        """Return the line with a day highlighted only within the bounds."""
        colored_text = line[bounds.start:bounds.end].replace(day, self.highlight(day))

        return line[:bounds.start] + colored_text + line[bounds.end:]

    def print_month(self, text_calendar: calendar.TextCalendar) -> None:
        """Print the current month."""
        date = datetime.date.today()
        month = text_calendar.formatmonth(date.year, date.month, w=0, l=0).splitlines()

        # Print year header and the days of the week.
        print(month[0])
        print(month[1])

        # Print weeks highlighting the current day of the month.
        # Pad day to two characters; ensures " 1" cannot match " 11".
        day = f"{date.day:>2}"

        # Stop after the first match; the same day number may appear in subsequent weeks.
        found_day = False

        for output in month[2:]:
            if not found_day and day in output:
                output = output.replace(day, self.highlight(day))
                found_day = True

            print(output)

    def print_quarter(self, text_calendar: calendar.TextCalendar) -> None:
        """Print all months in the current quarter."""
        date = datetime.date.today()
        month_name = calendar.month_name[date.month]
        quarter_bounds = self.get_quarter_column_bounds_for_month(date.month)
        year = text_calendar.formatyear(date.year, w=2, l=1, c=6, m=3).splitlines()  # Use defaults for consistency.

        # Print year header and empty line.
        print(year[0])
        print()

        # Find current quarter.
        quarter_header_index = 2

        for output in year[quarter_header_index:]:
            if month_name in output:
                break

            quarter_header_index += 1

        # Highlight current month name.
        year[quarter_header_index] = year[quarter_header_index].replace(month_name, self.highlight(month_name))

        # Print month names and weekdays.
        print(year[quarter_header_index])
        print(year[quarter_header_index + 1])

        # Print weeks highlighting the current day of the month.
        # Pad day to two characters; ensures " 1" cannot match " 11".
        day = f"{date.day:>2}"

        # Stop after the first match; the same day number may appear in subsequent weeks.
        found_day = False

        for output in year[quarter_header_index + 2:]:
            # An empty line marks the end of the quarter.
            if not output:
                break

            if not found_day and day in output[quarter_bounds.start:quarter_bounds.end]:
                output = self.highlight_day_within_bounds(output, day, quarter_bounds)
                found_day = True

            print(output)

    def print_year(self, text_calendar: calendar.TextCalendar) -> None:
        """Print all months in the current year."""
        date = datetime.date.today()
        month_name = calendar.month_name[date.month]
        quarter_bounds = self.get_quarter_column_bounds_for_month(date.month)
        year = text_calendar.formatyear(date.year, w=2, l=1, c=6, m=3).splitlines()  # Use defaults for consistency.

        # Print months highlighting the current month and day.
        # Pad day to two characters; ensures " 1" cannot match " 11".
        day = f"{date.day:>2}"

        # Day highlighting is restricted to the current month's column bounds.
        found_day, found_month = False, False

        for output in year:
            if not found_month and month_name in output:
                output = output.replace(month_name, self.highlight(month_name))
                found_month = True

            if not found_day and found_month and day in output[quarter_bounds.start:quarter_bounds.end]:
                output = self.highlight_day_within_bounds(output, day, quarter_bounds)
                found_day = True

            print(output)


def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return When().run()


if __name__ == "__main__":
    raise SystemExit(main())
