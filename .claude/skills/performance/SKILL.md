---
name: performance
description: Review one or more Python modules for practical performance improvements that are rubric-compliant and readability-preserving. Use when asked to check for performance optimizations or efficiency improvements.
---

This skill is activated when the user provides one or more Python module paths and asks for a performance review,
efficiency audit, or optimization check. Read each file directly from the filesystem using its path.

---

## Context: I/O-Bound Reality

Before reviewing, acknowledge this constraint: Pyr-CLI commands are **I/O bound**. The bottleneck is almost always disk
reads, terminal throughput, or subprocess communication — not Python computation. Any finding that would not
meaningfully reduce I/O wait time should be labeled **Low impact** and only recommended if the change is trivially safe.
Findings that increase code complexity without moving the I/O bottleneck should be labeled **Not recommended**.

---

## Rubric Compliance

All suggestions must remain consistent with the project's coding standards in `docs/code_evaluation_rubric.md`. Reject
any optimization that:

- Reduces readability without a meaningful payoff
- Introduces premature abstraction
- Violates the weakest-correct-type-annotation principle
- Replaces a clear construct with a clever one
- Adds error handling or fallbacks not warranted by the change

If a change would require a rubric deviation to implement, do not suggest it.

---

## Review Scope

### 1. Streaming vs. Buffering

The project strongly favors generators and streaming (`iter_*` functions, `Iterable` parameters). Check for:

- **Unnecessary list materialization** — `list(generator)` or `[x for x in ...]` followed by a single-pass iteration. If
  the caller only iterates once and does not need `len()`, indexing, or multiple passes, an `Iterable` or generator is
  correct.
- **`.readlines()` without justification** — buffering the full file into memory before processing. The project uses
  this intentionally in `--in-place` contexts (must buffer before overwriting the same file). Distinguish intentional
  from accidental use.
- **`list()` wrapping at call sites** — wrapping an already-streaming source in `list()` to satisfy a type annotation
  that is more concrete than the function requires. This is a type annotation problem, not a performance fix — flag it
  as a typing issue instead and refer to the `typing` skill.

Impact: **High** when processing large files; **Low** for small or bounded inputs.

### 2. Redundant Work in Loops

Check for values computed or looked up inside a loop body that are invariant across all iterations:

- **Deep attribute chains** — flag only when the chain is three or more levels deep (e.g.,
  `self.some_class.some_inner.key`) and the value is used multiple times in the loop body. Shallow lookups like
  `self.attr` or `self.args.attr` do not justify a local — the savings are negligible and the extra variable adds noise
  without clarifying intent.
- **Loop-invariant expressions with logic** — a boolean combination or method call computed from invariant inputs is
  worth hoisting when it both reduces repeated work and clarifies meaning. Example:
  `apply_style = self.use_color and not self.args.invert_match` set once before the loop is clearer and faster than
  re-evaluating the expression per line.
- **Repeated method calls returning a constant result** — e.g., `len(some_list)` called per iteration when the
  collection does not change.
- **Repeated module-level lookups** — calling a function that re-derives the same result on every iteration.

Only flag cases where the loop body is the hot path (processing lines, paths, or matches). Do not flag single-pass setup
code outside loops.

Impact: **Low** for typical CLI inputs; worth flagging if the loop processes every line of a potentially large file.

### 3. Compiled Regex in Loops

Verify that regex patterns are compiled **once** before any loop, not inside the loop body. The project pre-compiles via
`patterns.compile_patterns()` — confirm this pattern holds everywhere regex is used. A `re.compile()` call inside a loop
body that processes lines or paths is always a defect.

Impact: **High** — regex compilation is expensive and compounds linearly with input size.

### 4. Membership Testing Complexity

Check `in` tests against sequences when a set would be more appropriate:

- `value in some_list` inside a loop where `some_list` is large or grows — O(n) per test.
- `value in some_tuple` for a fixed set of values — replace with a `frozenset` constant or `match` statement.

For this project, pattern lists are typically small (user-provided, not large data structures), so these are usually *
*Low impact**. Flag only when the collection could be unbounded or is rebuilt on each test.

### 5. String Building

Check for incremental string construction inside loops:

- `result += fragment` in a loop — should be `"".join(fragments)` where `fragments` is a list built in the loop.
- Exception: single-append cases outside loops, or when the string is short and bounded.

Modern CPython optimizes some `+=` cases, but the `join` pattern is still correct and clearer for multi-fragment
assembly. Flag only when the loop runs over unbounded input.

Impact: **Low** in most CLI contexts.

### 6. Early Exit Opportunities

Check for loops or branches that could terminate early but do not:

- Iterating a full collection to find the first match when `next()` with a generator expression would suffice.
- Continuing to process input after a condition that makes further processing irrelevant (e.g., `--quiet` mode already
  raises `SystemExit`, but other commands may have similar all-or-nothing conditions).
- Nested loops where an inner condition could `break` the outer loop.

Flag only when skipping work is meaningful — not when the remaining iterations are trivially cheap.

Impact: Varies. **High** if the skipped work is proportional to input size; **Low** if the loop is small.

### 7. Unnecessary Recomputation of `len()` for Padding

A specific pattern common in this project: computing display padding via `len(str(last_item.line_number))` once, used
across many output lines. Verify this is cached before the print loop, not recomputed per line.

---

## What Not to Flag

- **Algorithmic rewrites** — do not suggest changing a correct O(n) algorithm to something more complex unless the
  current approach is genuinely O(n²) or worse.
- **`__slots__`** — not appropriate for command classes with dynamic `argparse` namespaces.
- **Lazy imports** — startup time is not a bottleneck for these tools.
- **C-extension or NumPy-style suggestions** — out of scope.
- **Anything that harms readability** — if the suggestion requires a comment to explain why it is correct, it is
  probably not worth doing.
- **Shallow attribute hoisting** — do not suggest `local = self.attr` or `local = self.args.attr` as loop-invariant
  locals. Savings are negligible for I/O-bound work, and naming a variable purely to cache a one- or two-level lookup
  adds noise that can obscure where the value comes from.

---

## Impact Labeling

Assign one of three labels to each finding:

- **High** — measurable gain for typical inputs (e.g., regex compilation in a line-processing loop, streaming instead of
  full-file buffering for large files).
- **Low** — real but modest gain; safe to apply if the change is trivially clean.
- **Not recommended** — technically valid but the readability cost exceeds the benefit for a CLI tool of this type.

---

## Output Format

### Per-module review

For each module, produce:

1. A brief I/O-bound context note: confirm whether the module's hot path is I/O or CPU bound, and what that means for
   the significance of the findings.
2. Specific findings in source order, each labeled with impact level and including a concrete before/after example where
   a change is recommended.
3. A **Summary** table at the end:

| Module | Location | Finding | Impact | Action |
|--------|----------|---------|--------|--------|

Only include rows for genuine findings. Do not pad with non-issues. If no actionable findings exist, say so explicitly.

### Tone

- Practical over pedantic — performance advice that ignores the I/O-bound reality of CLI tools is not useful.
- Be precise about what is being saved: memory allocation, CPU cycles, or I/O operations.
- When a finding is **Not recommended**, state why clearly — what the readability cost is and why it outweighs the
  benefit.
- Do not suggest changes that require touching more than a few lines of code per finding.
