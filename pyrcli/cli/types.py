"""Shared type aliases for CLI modules."""

import re
from collections.abc import Callable, Collection

#: Sequence of compiled regular expression patterns.
type CompiledPatterns = Collection[re.Pattern[str]]

#: Callback for reporting error messages.
type ErrorReporter = Callable[[str], None]

__all__ = (
    "CompiledPatterns",
    "ErrorReporter",
)
