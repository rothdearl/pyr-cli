"""Type aliases used by the progress package."""

from typing import Final, Literal

#: Message rendered alongside a progress indicator, or ``None`` for no message.
type ProgressMessage = str | None

#: Position of the message relative to the indicator.
type ProgressMessagePosition = Literal["left", "right"]

__all__: Final[tuple[str, ...]] = (
    "ProgressMessage",
    "ProgressMessagePosition",
)
