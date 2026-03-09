"""Type aliases used throughout the CLI framework."""

import re
from collections.abc import Callable, Sequence
from typing import Final

#: Sequence of compiled regular expression patterns.
type CompiledPatterns = Sequence[re.Pattern[str]]

#: Callback for reporting error messages.
type ErrorReporter = Callable[[str], None]

__all__: Final[tuple[str, ...]] = (
    "CompiledPatterns",
    "ErrorReporter",
)
