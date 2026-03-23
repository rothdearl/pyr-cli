# Python Code Evaluation Rubric and Design Guidelines

The following criteria define the expected design and review standards for modern, idiomatic, and maintainable Python
code. This rubric reflects preferred design principles and trade-offs, not an exhaustive list of universal Python
conventions. Evaluators must apply these criteria with judgment and context, particularly when reviewing public-facing
APIs or code that must remain compatible with legacy systems. The rubric is organized from foundations to surface
presentation: beginning with high-level development philosophy, then function behavior and control flow, followed by
typing and data modeling, and concluding with documentation and style.

---

## Development Philosophy (Zen of Python)

Code should, where practical, align with the principles captured in the Zen of Python (`import this`). These
principles — favoring clarity over cleverness, simplicity over unnecessary complexity, explicitness over implicit
behavior, and readability over density — represent a widely shared cultural foundation of idiomatic Python.

Evaluators should prefer designs that are straightforward to understand, easy to explain, and unsurprising to typical
experienced Python developers, even when such designs are not the most abstract or theoretically "pure". When trade-offs
arise between elegance, practicality, and maintainability, solutions that are clear, predictable, and minimally
surprising should generally be favored.

Evaluators should be pedantic but practical: precise about semantic contracts and correctness, while avoiding
unnecessary rigidity, over-abstraction, or formalism that does not materially improve clarity or maintainability.

Clarity and explicitness apply most strongly to semantic contracts (what is guaranteed), rather than to overly formal
prose. Documentation must be precise where correctness depends on it and otherwise written in clear, ordinary language.

---

## Language Version and Features

Code should target modern Python (≥ 3.12).

Legacy or deprecated patterns should be avoided unless explicitly justified.

Features introduced in Python 3.12 (or earlier) may be used when they meaningfully improve clarity, correctness, or
expressiveness.

### Standard Library Usage

Modern, well-supported standard library APIs should be used in preference to legacy or superseded alternatives when they
improve clarity, correctness, or maintainability.

When multiple standard library approaches are available, favor those aligned with current Python best practices and the
targeted language version.

---

## Import Policy (Sibling Modules and Shared State)

- Use relative imports for modules within the same package.
- When accessing or mutating shared runtime state, import the module itself (e.g., `from . import context`) and read
  attributes from the module namespace at use time. This preserves semantic correctness by ensuring the current value is
  observed and avoiding stale bindings.
- Import names directly (e.g., `from .auth import fetch_access_token_header`) for functions, classes, type aliases, and
  semantically constant values that are not expected to be rebound.
- Do not import mutable module variables directly (e.g., `from .context import hostname`). Direct name imports of
  mutable module state create local bindings that will not reflect subsequent updates to the module attribute.
- Prefer explicit imports to wildcard imports.
- Keep imports at module scope unless a local import is required to:
    - Avoid a circular dependency
    - Reduce import-time side effects
    - Defer an expensive or optional dependency

**Evaluator Heuristic:** If a value is intended to reflect shared, evolving module state, importing the module and
accessing the attribute dynamically is the correct semantic model. If importing a name would make the binding incorrect
after mutation, the import form is a design flaw.

---

## Function Design

- Functions should have a single primary responsibility.
- Functions should be Pythonic, readable, and free of common code smells.
- Functions should be efficient for their intended use, avoiding unnecessary work, while prioritizing readability and
  correctness over premature optimization.
- Functions must read clearly, behave predictably, and their documentation must match their actual behavior.
- Input normalization should be separated from core processing logic, unless separation would meaningfully harm clarity
  or performance.

### Parameter Ordering

Function parameters should be ordered to reflect the conceptual structure of the API rather than incidental
implementation details. Parameters should generally be declared in the following order:

1. **Primary subject** — the main object, entity, or resource the function conceptually acts upon.
2. **Data being operated on** — additional inputs that represent the information to be processed.
3. **Configuration** — flags, options, or settings that influence behavior.
4. **Optional collaborators** — auxiliary components such as loggers, callbacks, hooks, or observers.

This ordering should make the function's intent clearer at the call site and support more natural use of positional
arguments while keeping optional or infrastructural concerns toward the end of the signature.

### Keyword-only Parameters

- Use keyword-only parameters (`*`) for public functions that accept multiple optional, boolean, or configuration-style
  arguments. This improves call-site clarity and prevents positional ambiguity.
- Keyword-only parameters should be used when a parameter represents configuration, policy, or behavior control rather
  than primary data being operated on.
- Do not use keyword-only parameters for simple required lookups where positional order is natural and consistent with
  established standard-library conventions (e.g., `section`, `option`).
- Prefer keyword-only parameters when a function accepts a primary subject followed by semantically different inputs
  whose meaning is not obvious positionally.
- Keyword-only parameters improve call-site readability when:
    - Multiple arguments share the same type (e.g., `str`, `bool`, `int`)
    - Boolean flags would otherwise be passed positionally
    - Defaulted parameters control non-obvious behavior
- Overuse of keyword-only parameters for trivial or self-evident arguments is discouraged; the goal is semantic clarity,
  not mechanical uniformity.

**Evaluator Heuristic:** When a function has three or more parameters and more than one is optional or
configuration-like, keyword-only parameters should generally be used unless positional order is both conventional and
unambiguous.

- Avoid reassigning function parameters unless the function is very short and the intent is immediately obvious;
  instead, use local variables for transformations or intermediate values.

### Module-Level Functions vs. Utility Classes

Do not create a class solely to hold functions. Declare functions at module level instead; a class that carries no state
and provides no polymorphism adds ceremony without benefit.

A class is appropriate when it encapsulates state, participates in inheritance, or satisfies a protocol. A collection of
stateless functions with no shared lifecycle belongs at module scope.

An exception is a `@final` class used as a namespace for `Final` constants when grouping related constants
meaningfully (e.g., ANSI styling constants scoped to a command). This pattern is acceptable when the grouping improves
clarity over a flat list of module-level constants.

---

## Naming Conventions

### Function Naming

- Function names should clearly and accurately reflect their behavior.
- Function names, behavior, and documentation must be tightly aligned.
- Function names should describe the semantic result of the operation rather than the serialization format, parsing
  mechanism, or internal representation used to produce it.

#### Normalization Functions

Functions whose purpose is to transform input into a canonical form so downstream logic does not need to care about
superficial differences should include the word `normalize` or a clear synonym (e.g., `canonicalize`, `coerce`) in their
name.

#### Boolean Predicate Functions

- When a function's primary purpose is enforcing or validating conditions, naming should reflect that intent, even if a
  boolean is returned.
- Boolean-returning functions that perform validation, may raise errors, enforce conditions, or produce observable side
  effects should start with `check_` or another explicit verb such as `validate_` or `ensure_`.
- Pure boolean predicates without side effects should use conventional prefixes such as `is_`, `has_`, or `can_`.

#### Namespace Redundancy

Avoid repeating information already conveyed by the containing module or class (e.g., prefer `render.reverse_video()`
over `render.render_reverse_video()`) unless repetition prevents ambiguity.

**Evaluator Heuristic:** If the function's name, behavior, and documentation do not make its intent obvious, then
clarity has likely been sacrificed for brevity or convenience. Simple, explicit names that reduce the need to read
surrounding code are preferred to clever, compact, or context-dependent ones. When in doubt, evaluators should be
pedantic in service of readability.

### Variable Naming

- Variable names (including loop variables and comprehension bindings) should be chosen to communicate role and meaning,
  not merely satisfy syntax.
- Prefer descriptive, domain-relevant names over abbreviated or opaque names unless the abbreviation is a widely
  understood term in context.
- Avoid single-letter names except where convention strongly applies and readability is not harmed. Acceptable
  conventional cases include:
    - File handles in a `with open(...)` block (e.g., `as f`)
    - The throwaway name `_` for intentionally unused values
- Comprehension variables must follow the same naming standards as ordinary variables. In particular, the bound variable
  should reflect what each element represents, and names should not shadow built-ins or common standard-library
  identifiers unless explicitly justified.
- Constants should generally use `UPPER_SNAKE_CASE` when they are semantically constant.

**Evaluator Heuristic:** If a reader must examine surrounding lines of code to understand what a variable represents or
why it exists, then clarity has likely been sacrificed for brevity or convenience. Variable names that make their role
obvious at the point of use are preferred to shorter, context-dependent, or overly generic names; when in doubt,
evaluators should be pedantic in service of readability.

---

## Determinism and Side Effects

- Functions should be deterministic unless non-determinism is inherent to their purpose (e.g., randomness, I/O, or time)
  and clearly documented.
- Side effects should be explicit, minimal, and well-documented.
- Shared mutable module state must be accessed using module imports to preserve semantic correctness.

---

## Control Flow and Expressiveness

- Use modern language features (e.g., `match` statements) where they improve clarity over complex conditional logic.
- Code should favor explicit, readable control flow over cleverness.

### Ellipsis (`...`) vs. `pass`

The ellipsis expression (`...`) and the `pass` statement have distinct semantic meanings and should not be used
interchangeably.

- Use `...` to indicate that an implementation is intentionally absent. Appropriate contexts include:
    - Protocol method bodies
    - Abstract base class methods
    - Stub files (`.pyi`)
    - Type-only definitions or bodies that exist solely for typing purposes

  In these cases, `...` communicates that behavior is not defined here and is expected to be provided elsewhere.

- Use `pass` to indicate an intentional no-op. Appropriate contexts include:
    - Optional hooks or extension points
    - Default implementations that deliberately perform no action
    - Methods that are explicitly permitted to do nothing
    - Empty blocks that are syntactically required by Python (e.g., an empty `if`, `try`, or `class` body)

Under this rubric, `pass` signals that "nothing happens by design," whereas `...` signals that "this is unimplemented or
specification-only." Mixing these meanings is considered a style and expressiveness issue.

---

## Error Handling and Validation

- Exceptions should be specific and intentional.
- Broad `except Exception` clauses should be avoided unless used at well-defined boundaries.
- Exception chaining (`raise X(...) from err`) should be used when re-raising errors to preserve context.
- Errors should be reported through a consistent mechanism, and fallbacks must be documented.

---

## Typing and Type Design

Code should use current best-practice typing syntax, including:

- Built-in generics (e.g., `list[str]`, not `List[str]`)
- Prefer PEP 695 when defining reusable, generic APIs, not for trivial local functions
- `typing.Self`, `Protocol`, and `TypeAlias` when they improve API clarity

Type hints should prioritize clarity and correctness over completeness or exhaustiveness.

Enums should improve the semantic clarity of type signatures. Introducing an Enum that does not meaningfully restrict or
communicate valid choices is considered a design smell under this rubric.

**Evaluator Heuristic:** If removing an Enum from a type signature would not change how a caller reasons about valid
inputs or outputs, the Enum is likely misused.

### Collection Type Hints (PEP-Aligned)

Function parameters that accept collections must be typed using the weakest abstraction that correctly expresses the
function's semantic requirements, not merely the concrete implementation being passed.

This guidance aligns with PEP 484 (Type Hints), PEP 544 (Protocols and Structural Subtyping), and PEP 585 (Built-in
Generic Types), and reflects the design intent of the `collections.abc` hierarchy.

#### Preferred Abstract Collection Types

Listed roughly from weakest to strongest with respect to ordering and mutability:

**`Iterable[T]`**

- Use when the function only iterates over the values and makes no additional assumptions.
- Guarantees: `iter` only.
- Does not guarantee: length, boolean evaluation, membership testing, guaranteed reusability, indexing or ordering.
- Suitable for streaming, generator, or one-pass inputs.

**`Collection[T]`**

- Use when the function requires `len()`, membership testing, or other behaviors typically provided by `Collection`.
- Guarantees: `iter`, `len`, `contains`.
- Appropriate when `len()`, membership checks, or other `Collection`-like behaviors are used.

**`Sequence[T]`**

- Use when the function depends on ordering, positional meaning, or index-based access.
- Guarantees: stable ordering, indexing and slicing (`getitem`), repeatable iteration with positional consistency.
- Should not be used unless ordering or indexing is semantically required.

**`MutableSequence[T]`**

- Use when the function requires ordered, indexable access and in-place mutation of elements, but does not depend on a
  specific concrete container type.
- Guarantees: `iter`, `len`, `contains`, stable ordering, indexing, in-place element mutation.
- Does not guarantee support for `list`-specific APIs such as `list.sort()` or slice assignment.

**Concrete Collection Types (e.g., `list`, `tuple`, `set`)**

- Must only be used when required by the function's semantics, such as:
    - In-place mutation (e.g., `append`, `sort`, `pop`)
    - API contracts that require a specific type
    - Performance or memory characteristics unique to the implementation
- Using a concrete type when an abstract type would suffice is considered over-specification and a design flaw under
  this rubric.
- Structured tuples: concrete `tuple` types are appropriate when the structure or arity of the elements is semantically
  significant (e.g., `tuple[float, float]`).

**Evaluation Heuristic:** Type hints must describe how a function uses a collection, not what concrete type happens to
be passed today. The correct annotation is the weakest accurate type that captures the semantic guarantees the function
relies on. This principle applies most strictly to parameter types; return types may more often be concrete to
communicate allocation, ownership, or performance characteristics.

### Local Variable Type Hints

Local variable type hints are noise in the vast majority of cases — the type checker infers them from the assigned
value, and the annotation adds no information that a reader cannot already determine from context.

Local variable annotations are only justified when:

- The collection contains inner collections whose structure is not self-evident from `[]` or `{}` alone (e.g.,
  `list[list[str]]`, `dict[str, list[str]]`, `list[tuple[int, float | str]]`).
- A variable is declared without an initial value and assigned later, where the type would otherwise be `Unknown`.
- The inferred type is genuinely surprising and the annotation serves as documentation for the reader.

When annotating complex nested collection types, a type alias almost always improves clarity by naming the concept
rather than describing the structure.

---

## Asynchronous Code (When Applicable)

- `async` / `await` should be used correctly and consistently.
- Blocking operations should not be performed inside asynchronous functions.
- Async APIs should clearly signal their behavior through naming and documentation.

---

## Data Modeling

- Prefer structured types to ad-hoc dictionaries.
- Use `@dataclass` (preferably with `slots=True` and `frozen=True` where appropriate) for simple data containers.
- Immutability should be favored when practical.

### Enum Usage

- Enums should be used to model a closed set of meaningful choices within a domain.
- Enum members must represent valid options that are intentionally selected, passed into functions, returned from APIs,
  or otherwise participate in control flow or decision-making.
- Enums must not be used solely as namespaced containers for constants, configuration values, or unrelated symbolic
  values.
- If values are not conceptually chosen from, prefer:
    - Module-level constants
    - Typed constants (e.g., `Final[str]`, `Final[int]`)
    - Dedicated configuration objects or data structures
- The presence of an Enum in an API signals a constrained and meaningful domain. Introducing an Enum that does not
  provide this semantic restriction is considered a data modeling flaw under this rubric.

---

## Documentation and Docstrings

### General Requirements

- All public modules, classes, and functions must include docstrings.
- Docstrings should describe behavior and guarantees, not merely restate names or types.
- Documentation should be written in a structured docstring format. Google style is the preferred style, though NumPy or
  reStructuredText styles are acceptable alternatives if used consistently.
- Function docstrings should be written in the imperative mood (e.g., "Return the parsed value." rather than "Returns
  the parsed value.").
- Docstrings should be precisely pedantic about behavior and guarantees, while generally avoiding pedantry about
  ordinary English phrasing.

### Mood and Style

- **Module docstrings** should be written in the indicative mood, clearly describing what the module provides, defines,
  or implements.
- **Class docstrings** should be written in the indicative mood, typically as a noun phrase or descriptive statement,
  clearly describing what the class represents or encapsulates.
- **Function docstrings** should be written in the imperative mood using clear, ordinary prose and complete sentences.

### One-Line Docstrings

A one-line docstring must be used when the behavior can be completely described in a single, non-redundant sentence. The
summary line should clearly describe the observable behavior of the function.

### Parameter Documentation

The `:param` field should only be used when it provides meaningful clarification beyond the parameter name and type.
Avoid documenting parameters when doing so merely repeats information already obvious from the function signature.

### Behavioral Details and Bullet Lists

When additional behavioral details are required, prefer documenting them using bullet points within the docstring body
rather than introducing `:param`, `:return:`, or `:raises:` fields that merely restate obvious information.

Bullet points should be used to describe behavioral guarantees such as:

- Errors handled or suppressed
- Conditions under which values are returned or skipped
- Iteration or yielding semantics
- Lifetime or validity of returned objects
- Side effects or configuration interactions

### Return Value Documentation

Return behavior should be documented when it would not be obvious from the function name and signature. This may be done
either directly in the summary sentence, or using bullet points describing the structure and semantics of the returned
value. The `:return:` field should only be used when it adds meaningful clarity that cannot be expressed naturally in
the summary or bullet points.

### Exception Documentation

Use `:raises:` only when the exception is not obvious from the implementation or function purpose, or when documenting
the exception is necessary to understand correct usage. Avoid documenting obvious exceptions raised by underlying
library functions unless they are intentionally part of the public contract.

### Redundancy Guidelines

Documentation should avoid repeating information that is already clear from function names, parameter names, type
annotations, or surrounding context. When redundancy exists, prefer documenting behavior and guarantees rather than
repeating structural details.

### Describing Boolean Conditions

- Use **"enabled"** / **"disabled"** for boolean instance attributes that represent a feature or capability state.
- Use **"set"** for `argparse` boolean flags (`store_true` / `store_false`) that are either present or absent on the
  command line.
- Use **"provided"** or **"specified"** for `argparse` options that may be `None` if not provided at all.

### Describing Function Calls in Docstrings

Use **"Calls"** as the standard verb when documenting that a function calls another function or method (e.g., "Calls
`on_error(message)` if the file cannot be read."). Do not use "Invokes" — "Calls" is the more natural and idiomatic
English term and is consistent with Python's own documentation conventions.

**Evaluator Heuristic:**

- Prefer clear function names and signatures so docstrings can remain short.
- Docstring mood is correct: modules and classes use indicative mood; functions use imperative mood.
- Docstrings describe behavior, not implementation details.
- Prefer one-line docstrings whenever possible.
- Use bullet points for behavioral guarantees and non-obvious details.
- Use `:param`, `:return:`, and `:raises:` only when they add real clarity.
- Document behavior, side effects, and guarantees, not obvious syntax.
- If additional wording would not change how a competent caller uses the function, it is likely unnecessary.
- The docstring describes observable behavior rather than internal implementation details. The implementation could
  change without requiring the docstring to change.

---

## Style and Readability

### Comments

- Comments must be technically accurate, precise, and concise. They should document intent and reasoning rather than
  restate implementation. If a comment merely repeats what the code does, it should be removed or the code should be
  clarified.
- Prefer clear naming and structure over explanatory comments; comments are a fallback when the intent cannot be made
  obvious through code alone.
- Use comments to document:
    - Non-obvious business rules or edge cases
    - Workarounds for library or platform behavior
    - Performance tradeoffs or design decisions
    - The intent behind unusual or intentionally complex code
- Do not repeat information that is already clear from identifiers or structure.
- Use comments to explain option interactions, constraints, or other non-obvious behavior.

### String Formatting

#### Implicit String Literal Concatenation

- Use implicit string literal concatenation (adjacent string literals within parentheses) when:
    - Formatting involves multiple semantic segments (e.g., style → value → delimiter → reset).
    - ANSI/SGR styling or other visual formatting increases horizontal density.
    - Multi-line structure improves readability.
- Avoid implicit concatenation when:
    - Formatting is trivial (e.g., a single formatted value and literal).
    - The resulting structure would be less readable than a single f-string.
- Never mix implicitly concatenated strings with commas unless tuple construction is intentional.
- F-strings are appropriate for inline formatting passed to `print()`, `.replace()`, logging, and similar functions,
  when interpolation improves clarity.

**Evaluator Heuristic:** An inline f-string is acceptable when it represents a single logical unit and remains readable.
If it contains three or more semantic segments (e.g., style → value → reset) or begins to wrap, prefer implicit
concatenation or a named local variable for the formatted value.

- Avoid unnecessary f-strings: prefix a string with `f` only when it contains an interpolation (`{...}`). Remove the `f`
  after refactors that eliminate formatted expressions.
