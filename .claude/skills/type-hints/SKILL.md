---
name: type-hints
description: Review type hint usage across one or more Python modules, checking collection abstraction level, local variable annotation noise, type alias usage, and syntax currency. Use when asked to review or audit type hints or type annotations.
---

This skill is activated when the user provides one or more Python module paths and asks for a type hint review, type
annotation audit, or typing check. Read each file directly from the filesystem using its path.

---

## Rubric Reference

Before reviewing, read the **Typing and Type Design** section of:

```
docs/code_evaluation_rubric.md
```

The relevant section covers collection type hints, local variable annotations, and when to use type aliases. Apply it as
the authoritative standard.

---

## Review Scope

For every module provided, check each of the following areas:

### 1. Collection Parameter Abstraction

Collection parameters must be typed with the weakest abstraction that correctly expresses the function's semantic
requirements — not the concrete type that happens to be passed at the call site.

Work through each function parameter typed as a collection. For each one, determine what the function actually does with
it:

- **Only iterates** → `Iterable[T]`
- **Requires `len()`, membership testing, or reusable iteration** → `Collection[T]`
- **Requires stable ordering or index-based access** → `Sequence[T]`
- **Requires in-place mutation (`.append()`, `.insert()`, `del`)** → `MutableSequence[T]`
- **Requires list-specific behavior (`.sort()`, slice assignment) or a specific concrete API contract** →
  `list[T]` or other concrete type

Flag any parameter typed more concretely than its usage requires. Suggest the correct abstraction and explain why.

### 2. Return Type Concreteness

Return types may be more concrete than parameter types to communicate allocation, ownership, or performance
characteristics. A function that allocates and returns a new `list` may correctly annotate its return type as `list[T]`
even if the caller could treat it as `Sequence[T]`.

Flag return types that are:

- Abstract when concreteness would communicate meaningful ownership or allocation information.
- Concrete when the return type is a protocol or structural type that is meaningfully more restrictive (rare — flag only
  if clearly wrong).

### 3. Local Variable Annotation Noise

Local variable type annotations are justified only in these cases:

- The variable holds a nested or non-self-evident collection (e.g., `list[list[str]]`, `dict[str, list[str]]`,
  `list[tuple[int, float | str]]`).
- The variable is declared without an initial value and assigned later.
- The inferred type would genuinely surprise a reader.

Flag any annotation that does not meet one of these criteria. Scalar annotations, simple list/dict literal annotations
where the element type is obvious, and annotations that merely restate what the assignment shows are all noise.

### 4. Type Alias Usage

When a local variable annotation is justified and the type is a complex nested collection, a named type alias is almost
always preferred over an inline annotation. The alias names the concept rather than describing the structure.

The project uses PEP 695 `type` alias syntax:

```python
#: Lines sharing the same comparison key.
type _LineGroups = list[list[str]]
```

Flag justified annotations of complex nested types that are missing a type alias. Suggest an alias name that describes
the concept, not the structure.

### 5. Syntax Currency

All type hints must use modern Python ≥ 3.12 syntax:

- Built-in generics: `list[str]`, `dict[str, int]` — not `List[str]`, `Dict[str, int]`
- Union: `X | Y` — not `Union[X, Y]` or `Optional[X]`
- `typing.Self` for self-referential return types
- `typing.override` on overriding methods
- PEP 695 `type X = ...` for type aliases — not `TypeAlias`

Flag any legacy or deprecated annotation syntax.

### 6. `__all__` Annotation

`__all__` must not carry a type annotation. The convention carries the meaning.

Flag any `__all__: list[str] = (...)` or similar annotation.

---

## Output Format

### Per-module review

For each module, produce:

1. A brief overall assessment (one or two sentences).
2. Specific findings organized by function, class, or module-level location, in source order.
3. A **Summary of Required Changes** table at the end:

| Module | Location | Issue | Action |
|--------|----------|-------|--------|

Only include rows for genuine issues. Do not pad with non-issues.

### Tone

- Pedantic but practical.
- When a parameter type is over-specified, name the correct abstraction and state which operation(s) the function
  actually performs that determine the correct level.
- When a local annotation is noise, say what the type checker infers and why the annotation adds nothing.
- When a type alias is warranted, suggest a name.
- Be succinct. Do not repeat the same pattern across multiple locations unless the repetition itself is worth noting.
