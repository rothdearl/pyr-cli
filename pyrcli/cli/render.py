"""Utilities for styling text with ANSI escape sequences."""

import re
from collections.abc import Collection
from typing import Final

from .ansi import RESET, TextAttributes


def bold(text: str) -> str:
    """Return ``text`` rendered in bold."""
    return style(text, ansi_style=TextAttributes.BOLD)


def dim(text: str) -> str:
    """Return ``text`` rendered in dim."""
    return style(text, ansi_style=TextAttributes.DIM)


def reverse_video(text: str) -> str:
    """Return ``text`` rendered with reversed foreground and background colors."""
    return style(text, ansi_style=TextAttributes.REVERSE)


def style(text: str, *, ansi_style: str) -> str:
    """Return ``text`` rendered with the given ANSI style, reset afterward."""
    return f"{ansi_style}{text}{RESET}"


def style_pattern_matches(text: str, *, patterns: Collection[re.Pattern[str]], ansi_style: str) -> str:
    """Return ``text`` rendered with the given ANSI style, reset afterward."""
    # Avoid allocation and iteration for the common empty case.
    if not patterns:
        return text

    match_ranges = []

    for pattern in patterns:
        for match in pattern.finditer(text):
            match_ranges.append((match.start(), match.end()))

    # Merge overlapping match ranges to prevent nested ANSI codes from corrupting the output.
    merged_match_ranges = []

    for start, end in sorted(match_ranges):
        if merged_match_ranges and start <= merged_match_ranges[-1][1]:
            merged_match_ranges[-1] = (merged_match_ranges[-1][0], max(merged_match_ranges[-1][1], end))
        else:
            merged_match_ranges.append((start, end))

    # Style match ranges.
    styled_text = []
    prev_end = 0

    for start, end in merged_match_ranges:
        if prev_end < start:
            styled_text.append(text[prev_end:start])

        styled_text.extend([ansi_style, text[start:end], RESET])
        prev_end = end

    if prev_end < len(text):
        styled_text.append(text[prev_end:])

    return "".join(styled_text)


__all__: Final[tuple[str, ...]] = (
    "bold",
    "dim",
    "reverse_video",
    "style",
    "style_pattern_matches",
)
