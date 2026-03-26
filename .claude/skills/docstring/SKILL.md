---
name: docstring
description: Review or generate docstrings for Python modules, classes, or functions in isolation. Use when asked to review, write, fix, or improve docstrings without a full module evaluation.
---

This skill is activated when the user asks to review, write, fix, or improve docstrings — either for a whole module or
for specific functions or classes. Read each target file directly from the filesystem using its path before proceeding.

---

## Mode: Review

When the user asks to review existing docstrings, check every module, class, and function docstring against the
standards below. Do not evaluate naming, type hints, logic, or any other concern — docstrings only.

## Mode: Generate

When the user asks to write or generate missing docstrings, produce a docstring for each undocumented public module,
class, or function. Apply the same standards. Present each generated docstring inline — do not apply changes without
confirmation unless the user has asked you to write them directly.

---

## Standards

### Mood

- **Module docstrings** — indicative mood. Describe what the module provides, defines, or implements.
- **Class docstrings** — indicative mood. Describe what the class represents or encapsulates.
- **Function docstrings** — imperative mood. "Return the parsed value." not "Returns the parsed value."

### Length

- Use a one-line docstring when the behavior can be fully described in a single, non-redundant sentence.
- Use bullets for non-obvious behavioral contracts only: failure conditions, side effects, lifetime constraints,
  iteration semantics, or conditions under which values are skipped or returned.
- Do not use bullets merely to restate the signature or annotate every parameter.

### What to document

Document observable behavior and guarantees. Do not document implementation details — the docstring should remain
accurate if the implementation changes.

Document:

- What is returned and under what conditions, when not obvious from the name.
- Side effects or configuration state that the function modifies.
- Conditions under which `on_error` is called, when the function accepts an `ErrorReporter`.
- Iteration or yielding semantics for generators.
- Lifetime or validity constraints on returned objects.

Do not document:

- Information already clear from the function name, parameter names, or type annotations.
- What the code visibly does — only what it guarantees.
- Parameters or return values whose purpose is self-evident.

### `:param`, `:return:`, `:raises:`

Use these fields only when they add meaningful clarity that cannot be expressed naturally in the summary sentence or
bullet points. Do not use them to restate obvious information.

### Boolean conditions

Use precise language when describing boolean state:

- **"enabled"** / **"disabled"** — for boolean instance attributes representing a feature state.
- **"set"** — for `argparse` `store_true` / `store_false` flags.
- **"provided"** / **"specified"** — for `argparse` options that may be `None` if absent.

### Calling other functions

Use **"Calls"** — not "Invokes" — when documenting that a function calls another function or method.

---

## Output Format

### Review mode

For each module, list findings in source order. For each finding:

- Identify the location (module, class name, or function name).
- State the issue precisely (wrong mood, redundant content, missing contract, etc.).
- Provide the corrected docstring inline.

End with a summary table:

| Location | Issue | Corrected Docstring |
|----------|-------|---------------------|

Only include rows for genuine issues.

### Generate mode

Present each generated docstring with its location and the proposed text. Group by module if multiple files are
provided. Wait for confirmation before writing to disk unless the user has asked for direct application.
