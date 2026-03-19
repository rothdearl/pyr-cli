"""Shared type aliases for CLI modules."""

import re
from collections.abc import Callable, Sequence

#: Sequence of compiled regular expression patterns.
type CompiledPatterns = Sequence[re.Pattern[str]]

#: Callback for reporting error messages.
type ErrorReporter = Callable[[str], None]

__all__ = (
    "CompiledPatterns",
    "ErrorReporter",
)
