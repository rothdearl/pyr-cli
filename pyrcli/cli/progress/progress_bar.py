"""Terminal progress bar for tracking work with a known total."""

from dataclasses import dataclass, field
from typing import ClassVar, final, override

from pyrcli.cli import RESET
from ._base import _ProgressIndicator
from .types import ProgressMessage


@final
@dataclass(kw_only=True, slots=True)
class ProgressBarLayout:
    """Configuration for rendering a terminal progress bar.

    Attributes:
        width: Number of character cells used for the bar body.
        fill: Glyph used to represent completed progress.
        empty: Glyph used to represent remaining progress.
        left_delimiter: Left delimiter placed before the bar body.
        right_delimiter: Right delimiter placed after the bar body.
        show_percent: Whether to append a percentage suffix (value followed by ``%``).
        percent_style: ANSI SGR prefix applied to the percent value (empty disables styling).
        percent_symbol_style: ANSI SGR prefix applied to the percent symbol (empty disables styling).
        percent_reset: ANSI reset sequence appended after the percent suffix; empty disables automatic reset.
    """
    _DEFAULT_WIDTH: ClassVar[int] = 20

    width: int = _DEFAULT_WIDTH
    fill: str = "·"
    empty: str = " "
    left_delimiter: str = "["
    right_delimiter: str = "]"
    show_percent: bool = True
    percent_style: str = ""
    percent_symbol_style: str = ""
    percent_reset: str = RESET

    def __post_init__(self) -> None:
        """Initialize and normalize configuration."""
        if self.width <= 0:
            self.width = self._DEFAULT_WIDTH


@final
@dataclass(kw_only=True, slots=True)
class ProgressBar(_ProgressIndicator):
    """Terminal progress bar for tracking work with a known total.

    - Updates the rendered bar when progress advances.
    - Clamps progress to ``[0, total]`` when ``total > 0``; otherwise renders as permanently 100%.
    - On finalization:

      - Retains or clears the bar according to ``clear_on_finish``.
      - Prints a terminating newline when visible and not cleared.
      - Writes a final message followed by a newline when the message is non-empty, even when the indicator is not visible.
    - Treats ``None`` and empty strings as no message.

    Attributes:
        total: Total number of units representing 100% completion (non-positive values render as permanently 100%).
        layout: Rendering layout for the progress bar.
        clear_on_finish: Whether to clear the progress bar on finalization (message behavior is unchanged).
    """

    total: int
    layout: ProgressBarLayout = field(default_factory=ProgressBarLayout)
    clear_on_finish: bool = False
    _completed: int = field(default=0, init=False, repr=False)

    def _completion_fraction(self, completed: int) -> float:
        """Return the fraction of work completed, or ``1.0`` if ``total <= 0``."""
        if self.total <= 0:
            return 1.0

        return completed / self.total

    def _render_bar(self, fraction: float) -> str:
        """Return a rendered progress bar for a completion fraction in ``[0, 1]``."""
        filled_cells = round(fraction * self.layout.width)
        empty_cells = self.layout.width - filled_cells
        bar = (
            f"{self.layout.left_delimiter}"
            f"{self.layout.fill * filled_cells}"
            f"{self.layout.empty * empty_cells}"
            f"{self.layout.right_delimiter}"
        )

        if not self.layout.show_percent:
            return bar

        return f"{bar} {self._render_percent(round(fraction * 100))}"

    @override
    def _render_final(self, message: ProgressMessage) -> None:
        """Render the final indicator state and terminate the line when appropriate."""
        if self.clear_on_finish:
            self._finalize_with_message(message)
            return

        bar = self._render_bar(self._completion_fraction(self._completed))

        self._writer.write_indicator_line(indicator=bar, message=message, position=self.message_position)
        self._writer.newline()

    def _render_percent(self, percent: int) -> str:
        """Return a percent suffix (e.g., ``100%``), applying layout SGR styles when configured."""
        return (
            f"{self.layout.percent_style}"
            f"{percent:3d}"
            f"{self.layout.percent_symbol_style}%"
            f"{self.layout.percent_reset}"
        )

    def advance(self, step: int = 1, *, message: ProgressMessage = None) -> None:
        """Advance progress by ``step`` units and redraw the bar."""
        self.update(self._completed + step, message=message)

    def complete(self) -> None:
        """Mark all units as completed and redraw the bar."""
        self.update(self.total)

    def start(self, *, message: ProgressMessage = None) -> None:
        """Render the initial 0% progress state with an optional message.

        - Does not advance the progress value.
        """
        self.update(0, message=message)

    def update(self, completed: int, *, message: ProgressMessage = None) -> None:
        """Set progress to ``completed`` units and redraw the bar."""
        if self._finished:
            return

        # Clamp progress to the valid range.
        if self.total <= 0:
            clamped = max(0, completed)
        else:
            clamped = max(0, min(self.total, completed))

        bar = self._render_bar(self._completion_fraction(clamped))

        self._writer.write_indicator_line(indicator=bar, message=message, position=self.message_position)
        self._completed = clamped


__all__ = (
    "ProgressBar",
    "ProgressBarLayout",
)
