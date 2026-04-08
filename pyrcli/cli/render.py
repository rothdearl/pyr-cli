"""Utilities for styling text with ANSI escape sequences."""

import re
from collections.abc import Collection

from .ansi import RESET, TextAttributes

# Start and end character position pair representing a match range.
type _MatchRange = tuple[int, int]


def _collect_merged_match_ranges(text: str, *, patterns: Collection[re.Pattern[str]]) -> list[_MatchRange]:
    """Return merged non-overlapping match ranges for all patterns within ``text``."""
    ranges: list[_MatchRange] = []

    for pattern in patterns:
        for match in pattern.finditer(text):
            ranges.append((match.start(), match.end()))

    # Merge overlapping ranges to prevent nested ANSI codes from corrupting the output.
    merged: list[_MatchRange] = []

    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    return merged


def bold(text: str) -> str:
    """Return ``text`` styled in bold."""
    return style(text, ansi_style=TextAttributes.BOLD)


def dim(text: str) -> str:
    """Return ``text`` styled at reduced intensity."""
    return style(text, ansi_style=TextAttributes.DIM)


def reverse_video(text: str) -> str:
    """Return ``text`` styled with reversed foreground and background colors."""
    return style(text, ansi_style=TextAttributes.REVERSE)


def style(text: str, *, ansi_style: str) -> str:
    """Return ``text`` styled with ``ansi_style``, resetting afterward."""
    return f"{ansi_style}{text}{RESET}"


def style_matches(text: str, *, patterns: Collection[re.Pattern[str]], ansi_style: str) -> str:
    """Return ``text`` with pattern matches styled using ``ansi_style``.

    - Overlapping matches are merged before styling.
    - Resets styling after each match.
    """
    # Avoid allocation and iteration for the empty case.
    if not patterns:
        return text

    styled_text = []
    prev_end = 0

    for start, end in _collect_merged_match_ranges(text, patterns=patterns):
        if prev_end < start:
            styled_text.append(text[prev_end:start])

        styled_text.extend([ansi_style, text[start:end], RESET])
        prev_end = end

    if prev_end < len(text):
        styled_text.append(text[prev_end:])

    return "".join(styled_text)


__all__ = (
    "bold",
    "dim",
    "reverse_video",
    "style",
    "style_matches",
)
