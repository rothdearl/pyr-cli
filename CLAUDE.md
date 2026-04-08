# CLAUDE.md — Pyr-CLI Project Context

This file provides context for Claude sessions working on the Pyr-CLI project. It summarizes the project's design
philosophy, coding standards, naming conventions, and documentation expectations. All guidance here reflects decisions
made and refined over the course of this project's development.

---

## Project Overview

Pyr-CLI is a toolkit of small, composable Unix-style CLI programs built on a shared Python framework. Each tool performs
one well-defined operation, favors explicit behavior over implicit defaults, and composes predictably in shell
pipelines.

**Package structure:**

- `pyrcli.cli` — the CLI framework (base classes, utilities, type aliases)
- `pyrcli.cli.http` — optional HTTP request helpers built on `requests`
- `pyrcli.cli.progress` — optional terminal progress indicators
- `pyrcli.commands` — command implementations (one module per command)

**Key framework modules:**

| Module            | Purpose                                               |
|-------------------|-------------------------------------------------------|
| `ansi.py`         | ANSI SGR escape sequence constants                    |
| `cli_program.py`  | `CLIProgram` base class and program lifecycle         |
| `env.py`          | Environment variable helpers                          |
| `ini.py`          | INI configuration file utilities                      |
| `io.py`           | File reading, writing, and path traversal             |
| `patterns.py`     | Regex pattern compilation and matching                |
| `platform.py`     | OS/platform predicates                                |
| `render.py`       | ANSI text styling utilities                           |
| `reporters.py`    | `ErrorReporter` factory functions                     |
| `terminal.py`     | Standard stream terminal predicates                   |
| `text.py`         | Text parsing, splitting, and normalization            |
| `text_program.py` | `TextProgram` base class for text-processing commands |
| `types.py`        | Shared type aliases                                   |

---

## Design Philosophy

The project is **pedantic but practical** — precise about semantic contracts and correctness, while avoiding unnecessary
rigidity or over-abstraction.

- Clarity over cleverness.
- Explicitness over implicit behavior.
- Simplicity over unnecessary complexity.
- Single responsibility at every level — modules, classes, and functions.
- Pure functions separated from I/O.
- Weakest correct type annotations for inputs; concrete types for return values when ownership matters.

The full design rubric is in `docs/code_evaluation_rubric.md`. The command-line help text rubric is in
`docs/help_text_rubric.md`. Both are authoritative references for all code and documentation decisions.

---

## Language and Target

- Python ≥ 3.12.
- Use modern syntax: `match` statements, PEP 695 type aliases (`type X = ...`), built-in generics (`list[str]`, not
  `List[str]`), `typing.Self`, `typing.override`.
- No legacy or deprecated patterns unless explicitly justified.

---

## Import Policy

Follow the Google Python Style Guide: import utility modules as modules and call functions with their module prefix.
This makes the origin of every call visible at the call site without reading the import block.

- Import **utility modules** as modules and call functions with the module prefix:

``` python
from pyrcli.cli import io, patterns, render, terminal, text
```

- Import **names directly** for classes, type aliases, and `Final` constants — not for functions. These names are
  self-identifying and do not benefit from a module prefix:
    - **Classes used as type annotations** (e.g., `from pyrcli.cli.io import InputFile`) — `input_file: InputFile` reads
      more naturally than `input_file: io.InputFile`.
    - **Namespace or enum-like constant classes** (e.g., `from pyrcli.cli.ansi import ForegroundColors`) —
      `ForegroundColors.BRIGHT_CYAN` already communicates the domain; a module prefix adds a redundant third level.
    - **Standalone constants** (e.g., `from pyrcli.cli.ansi import RESET`, `from pyrcli.cli.platform import IS_POSIX`) —
      short, unambiguous names used inline.

- Import **mutable shared state** via the module so attribute access reflects the current value at call time. The one
  example in this project is `_config` in `ini.py` — it must be accessed via the module, never imported directly.

- **Intra-package imports within `pyrcli/cli/`**: framework modules import sibling names directly using relative imports
  to avoid circular dependencies:

``` python
from .terminal import stdin_is_redirected
from .io import InputFile, open_text_files
```

---

## Naming Conventions

### Functions

- Names describe the **semantic result**, not the mechanism, serialization format, or internal representation.
- `normalize_*` or `canonicalize_*` for input normalization functions.
- `check_*`, `validate_*`, `ensure_*` for functions that validate, enforce conditions, or raise errors.
- `is_*`, `has_*`, `can_*` for pure boolean predicates with no side effects.
- Avoid namespace redundancy: `render.reverse_video()` not `render.render_reverse_video()`.

### Variables

- Descriptive and domain-relevant. Never single-letter except `f` for file handles in `with open(...)` and `_` for
  intentionally unused values.
- Comprehension variables follow the same standards as ordinary variables.
- Constants use `UPPER_SNAKE_CASE`.

### Boolean Conditions in Documentation

- **"enabled"** / **"disabled"** — for boolean instance attributes representing a feature state.
- **"set"** — for `argparse` `store_true` / `store_false` flags.
- **"provided"** / **"specified"** — for `argparse` options that may be `None` if absent.

---

## Type Hints

### Parameters

Use the **weakest accurate abstraction**:

- `Iterable[T]` — iteration only, no length or indexing required.
- `Collection[T]` — requires `len()` or membership testing.
- `Sequence[T]` — requires stable ordering or index-based access.
- `MutableSequence[T]` — requires in-place mutation without `list`-specific behavior.
- Concrete types (`list`, `tuple`, `set`) only when the semantics require it.

### Return types

May be more concrete to communicate allocation, ownership, or performance characteristics.

### Local variable annotations

Annotate only when genuinely necessary:

- Empty collection literals whose element type is **not self-evident** from context (e.g., `list[list[str]]`,
  `dict[str, list[str]]`).
- Variables declared without an initial value.
- When the inferred type would genuinely surprise a reader.

For complex nested types, define a **type alias** — it names the concept rather than describing the structure:

``` python
#: Lines sharing the same comparison key.
type _LineGroups = list[str]

#: Start and end character position pair representing a match range.
type _MatchRange = tuple[int, int]
```

Do **not** annotate scalar locals, simple list/dict literals whose types are obvious, or any variable where the
annotation merely restates what the assignment already shows.

### `__all__`

No type annotation. `__all__ = (...)` — convention carries the meaning.

---

## Function Design

### Parameter ordering

1. Primary subject
2. Data being operated on
3. Configuration (flags, options, settings)
4. Optional collaborators (callbacks, error reporters)

### Keyword-only parameters

Use `*` for public functions with multiple optional, boolean, or configuration-style arguments. Do not use for simple
required lookups where positional order is natural.

### Parameter reassignment

Avoid reassigning function parameters in non-trivial functions. Use a local variable instead.

---

## `CLIProgram` and `TextProgram` Lifecycle

```
parse arguments
→ option lifecycle
    check_option_dependencies()
    validate_option_ranges()
    normalize_options()
    initialize_runtime_state()
→ execute()
    (TextProgram manages input routing)
→ post_execute()  [TextProgram only]
→ exit_if_errors()
```

### TextProgram input routing

```
stdin redirected?
    yes:
        --stdin-files set? → read file names from stdin, process each file
        otherwise          → invoke handle_redirected_input() with stdin
        process any additional file arguments
    no:
        file arguments?    → process each file
        otherwise          → invoke handle_terminal_input()
post_execute() always called after processing completes.
```

### Key attributes

- `self.args` — initialized as `argparse.Namespace()`, never `None`.
- `self.use_color` — `True` only when `--color=on` and stdout is attached to a terminal.
- `self.encoding` — `"utf-8"` by default; `"iso-8859-1"` when `--latin1` is set.
- `self.has_errors` — set by `print_error()`; triggers non-zero exit via `exit_if_errors()`.

---

## Error Reporting

All I/O functions accept `on_error: ErrorReporter` — a `Callable[[str], None]`. Two standard reporters are provided:

``` python
reporters.raises(ValueError)  # raises exception_type with the message
reporters.suppress  # silently ignores the message
```

Error messages follow Unix conventions: `"{path!r}: reason"`.

---

## Documentation Standards

### Mood

- **Module docstrings** — indicative mood. Describe what the module provides.
- **Class docstrings** — indicative mood. Describe what the class represents.
- **Function docstrings** — imperative mood. "Return the value." not "Returns the value."

### One-liners vs. bullets

Prefer a one-line docstring when behavior can be fully described in a single sentence. Use bullets only for non-obvious
behavioral contracts — failure conditions, side effects, lifetime constraints, iteration semantics.

### What to document

Document observable behavior and guarantees. Never document implementation details — the docstring should remain
accurate if the implementation changes.

### What not to document

- Information already clear from the function name, parameter names, or type annotations.
- Parameters whose purpose is self-evident.
- Obvious exceptions from underlying library functions.

### Calling other functions

Use **"Calls"** — not "Invokes". Example: "Calls `on_error(message)` if the file cannot be read."

### Attributes block

Only document attributes whose behavior or contract is non-obvious. Do not document self-evident fields.

---

## Comments

Comments document **intent and reasoning**, not what the code does.

Use comments for:

- Non-obvious business rules or edge cases.
- Platform-specific workarounds.
- Order-dependent operations where the dependency is not obvious.
- Performance trade-offs or design decisions.

Remove comments that merely restate the code. If the code needs a comment to explain what it does, prefer renaming or
restructuring first.

---

## ANSI Styling

- `render.style(text, ansi_style=...)` — apply a style and reset.
- `render.style_matches(text, patterns=..., ansi_style=...)` — style pattern match ranges only.
- `render.bold(text)`, `render.dim(text)`, `render.reverse_video(text)` — convenience wrappers.
- Use implicit string concatenation for multi-segment styled strings (style → value → reset).
- Never apply ANSI styling unless `self.use_color` is `True`.

---

## Command Implementation Pattern

``` python
class MyCommand(TextProgram):  # or CLIProgram

    def __init__(self) -> None:
        super().__init__(name="mycommand")

    @override
    def build_arguments(self) -> argparse.ArgumentParser:
        """Return an argument parser describing the command-line interface."""
        ...

    @override
    def execute(self) -> None:  # CLIProgram only; TextProgram marks this @final
        """Execute the command using the prepared runtime state."""
        ...

    # TextProgram requires:
    @override
    def handle_redirected_input(self, input_lines: Iterable[str]) -> None: ...

    @override
    def handle_terminal_input(self) -> None: ...

    @override
    def process_input_file(self, input_file: InputFile) -> None: ...
```

**Entry point convention:**

``` python
def main() -> int | NoReturn:
    """Run the command and return the exit code."""
    return MyCommand().run()


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## Versioning

- Single project-wide version sourced from `pyrcli.__about__.__version__`.
- `CLIProgram` assigns it to `self.version` — use `self.version` in command implementations.
- Never hardcode or import `__version__` in individual command modules.
- `--version` flag: `version=f"%(prog)s {self.version}"`.
- Changes accumulate in `CHANGELOG.md` under `## Unreleased` and are promoted to a versioned section when a release is
  cut.
