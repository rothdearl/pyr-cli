"""Public API for the command-line interface framework."""

from .ansi import (
    BACKGROUND_COLORS_256,
    BackgroundColors,
    FOREGROUND_COLORS_256,
    ForegroundColors,
    RESET,
    TextAttributes,
)
from .cli_program import CLIProgram
from .ini import (
    get_bool_option,
    get_float_option,
    get_int_option,
    get_list_option,
    get_mapping_option,
    get_str_option,
    has_defaults,
    has_sections,
    is_empty,
    load_config,
)
from .io import (
    InputFile,
    iter_descendant_paths,
    iter_stdin_lines,
    open_text_files,
    write_text_file,
)
from .patterns import (
    compile_or_pattern,
    compile_patterns,
    matches_all_patterns,
)
from .platform import (
    IS_LINUX,
    IS_MACOS,
    IS_POSIX,
    IS_WINDOWS,
)
from .render import (
    bold,
    dim,
    reverse_video,
    style,
    style_pattern_matches,
)
from .reporters import (
    raises,
    suppress,
)
from .terminal import (
    stderr_is_redirected,
    stderr_is_terminal,
    stdin_is_redirected,
    stdin_is_terminal,
    stdout_is_redirected,
    stdout_is_terminal,
)
from .text import (
    decode_python_escape_sequences,
    iter_nonempty_lines,
    iter_normalized_lines,
    split_csv,
    split_pattern,
    split_shell_tokens,
    strip_trailing_newline,
)
from .text_program import TextProgram
from .types import (
    CompiledPatterns,
    ErrorReporter,
)

__all__ = (
    # ansi
    "BACKGROUND_COLORS_256",
    "BackgroundColors",
    "FOREGROUND_COLORS_256",
    "ForegroundColors",
    "RESET",
    "TextAttributes",

    # base classes
    "CLIProgram",
    "TextProgram",

    # ini
    "get_bool_option",
    "get_float_option",
    "get_int_option",
    "get_list_option",
    "get_mapping_option",
    "get_str_option",
    "has_defaults",
    "has_sections",
    "is_empty",
    "load_config",

    # io
    "InputFile",
    "iter_descendant_paths",
    "iter_stdin_lines",
    "open_text_files",
    "write_text_file",

    # patterns
    "compile_or_pattern",
    "compile_patterns",
    "matches_all_patterns",

    # platform
    "IS_LINUX",
    "IS_MACOS",
    "IS_POSIX",
    "IS_WINDOWS",

    # render
    "bold",
    "dim",
    "reverse_video",
    "style",
    "style_pattern_matches",

    # reporters
    "raises",
    "suppress",

    # terminal
    "stderr_is_redirected",
    "stderr_is_terminal",
    "stdin_is_redirected",
    "stdin_is_terminal",
    "stdout_is_redirected",
    "stdout_is_terminal",

    # text
    "decode_python_escape_sequences",
    "iter_nonempty_lines",
    "iter_normalized_lines",
    "split_csv",
    "split_pattern",
    "split_shell_tokens",
    "strip_trailing_newline",

    # types
    "CompiledPatterns",
    "ErrorReporter",
)
