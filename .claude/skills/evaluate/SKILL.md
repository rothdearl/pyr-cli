---
name: evaluate
description: Evaluate one or more Python modules against the project's coding standards, naming conventions, documentation requirements, and design philosophy. Use when asked to evaluate, review, or audit a module.
---

This skill is activated when the user provides one or more Python module paths and asks for an evaluation, code review,
or rubric check. Read each file directly from the filesystem using its path.

---

## Rubric Reference

Before evaluating, read the rubric at:

```
docs/code_evaluation_rubric.md
```

This is the authoritative reference for all evaluation decisions. Apply it with judgment — pedantic but practical.

---

## Evaluation Scope

Unless the user specifies otherwise, evaluate all the following for every module:

- **Module name and docstring** — does the name reflect the module's responsibility? Does the docstring describe what
  the module provides in indicative mood?
- **Module cohesion** — does the module contain only relevant functions? Styling functions do not belong in I/O modules,
  for example.
- **Class names and docstrings** — do names match behavior and function? Are docstrings in indicative mood?
- **Function names** — are they clear, idiomatic, and do they describe the semantic result rather than the mechanism,
  serialization format, or internal representation?
- **Function docstrings** — are they in imperative mood? Succinct? Do they describe behavior and guarantees, not
  implementation details?
- **Comments** — are they accurate, succinct, and explaining intent rather than restating code?
- **Variable names** — are they idiomatic? Is their purpose and function easily inferred without reading surrounding
  code?
- **Type hints** — are collection parameters typed with the weakest accurate abstraction? Are return types appropriately
  concrete? Are local variable annotations noise or genuinely justified?
- **Import policy** — are stable names imported directly? Is mutable shared state accessed via module import?
- **`pass` vs `...`** — are they used with correct semantic intent?
- **Namespace redundancy** — are function or class names repeating information already conveyed by the module or class?

---

## Evaluation Standards

Apply these project-specific standards consistently:

### Naming

- Function names describe the **semantic result**, not the mechanism.
- `normalize_*` / `canonicalize_*` for normalization functions.
- `check_*` / `validate_*` / `ensure_*` for functions that validate, enforce conditions, or may raise.
- `is_*` / `has_*` / `can_*` for pure boolean predicates with no side effects.
- No namespace redundancy: `render.reverse_video()` not `render.render_reverse_video()`.

### Docstrings

- **Modules and classes** — indicative mood.
- **Functions** — imperative mood. "Return the value." not "Returns the value."
- One-liner when behavior fits in a single non-redundant sentence.
- Bullets only for non-obvious behavioral contracts: failure conditions, side effects, lifetime constraints, iteration
  semantics.
- Never document what is already clear from the name, parameters, or type annotations.
- Use **"Calls"** not "Invokes" when referencing another function.

### Boolean conditions in documentation

- **"enabled"** / **"disabled"** — for boolean instance attributes.
- **"set"** — for `argparse` `store_true` / `store_false` flags.
- **"provided"** / **"specified"** — for `argparse` options that may be `None`.

### Comments

- Document intent and reasoning, not what the code does.
- Remove comments that restate the code.
- Keep comments that explain: non-obvious business rules, platform workarounds, order-dependent operations, performance
  trade-offs.

### Type hints

- Parameters: weakest accurate abstraction (`Iterable`, `Collection`, `Sequence`, `MutableSequence`, then concrete).
- Return types: may be concrete to communicate allocation or ownership.
- Local variable annotations: only for empty collection literals with non-obvious element types (e.g.,
  `list[list[str]]`, `dict[str, list[str]]`). Use a type alias when the structure is complex.
- `__all__` — no type annotation.

### Utility classes

- Do not create a class solely to hold functions. Module-level functions are preferred.
- Exception: `@final` classes used as namespaces for `Final` constants (e.g., `_Styles`) are acceptable when grouping
  improves clarity.

---

## Output Format

### Per-module evaluation

Evaluate each module in turn. For each module:

1. Brief summary of overall quality (one or two sentences).
2. Specific findings organized by function or class, in source order.
3. A **Summary of Required Changes** table at the end:

| Module | Location | Issue | Action |
|--------|----------|-------|--------|

Only include rows for genuine issues. Do not pad with non-issues.

### Tone

- Pedantic but practical.
- Precise about semantic contracts.
- Avoid unnecessary rigidity — if a deviation is justified by context, say so.
- When suggesting a docstring or name change, provide the suggested replacement inline.
- Be succinct. Do not repeat the same issue across multiple locations unless the pattern is worth calling out
  explicitly.

---

## Project Context

This project is **Pyr-CLI** — a toolkit of small, composable Unix-style CLI programs built on a shared Python framework.
Key conventions:

- Python ≥ 3.12. Use modern syntax: `match`, PEP 695 type aliases, built-in generics, `typing.Self`, `typing.override`.
- All commands inherit from `CLIProgram` or `TextProgram`.
- `self.args` is initialized as `argparse.Namespace()`, never `None`.
- `self.use_color` — boolean attribute, use "enabled/disabled" in documentation.
- `argparse` flags — use "set" in documentation.
- Error reporting uses `ErrorReporter` callbacks (`on_error`), not exceptions at the framework level.
- `pass` in optional hook methods signals intentional no-op. `...` in abstract methods signals unimplemented.
- The `_Styles` and `_Whitespace` namespace classes in command modules are intentional exceptions to the utility class
  rule.
