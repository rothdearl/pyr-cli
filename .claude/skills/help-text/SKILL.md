---
name: help-text
description: Evaluate or generate argparse help text for Pyr-CLI commands against the project's help text rubric. Use when asked to review, write, fix, or improve command-line help text or option descriptions.
---

This skill is activated when the user asks to review, write, fix, or improve argparse help text — either for an entire
command or for specific options or descriptions. Read the target file directly from the filesystem using its path before
proceeding.

---

## Rubric Reference

Before reviewing or generating, read the full rubric at:

```
docs/help_text_rubric.md
```

This is the authoritative reference for all decisions. Apply it with judgment — pedantic but practical.

---

## Mode: Review

When the user asks to review existing help text, evaluate every component below against the rubric. Do not evaluate code
logic, type hints, or any concern outside of help text.

### What to check

**Program description**

- Single concise sentence, preferably a verb phrase.
- No marketing language or implementation details.

**Option names**

- Short options are a single letter.
- Long options use kebab-case — no camelCase, underscores, or dots.

**Metavariables**

- Uppercase (`FILE`, `N`, `SEP`, `PATTERN`, `FMT`).
- Explicitly set via `metavar=` in argparse when the default would be wrong or unclear.

**Option descriptions — apply the checklist from the rubric for each option:**

- Infinitive mood — begins with a bare verb, no explicit subject.
- Action phrase first — modifier clause, if any, follows in parentheses.
- POSIX/Unix terminology — standard nouns (`file`, `line`, `field`, `pattern`, `count`, `separator`).
- Manpage economy — no filler words or unnecessary articles; articles retained when their removal reads unnaturally.
- Defaults documented when non-obvious; omitted when trivial or self-evident.
- Constraints documented in consistent parentheses: `(default: X; N >= Y)` — default listed first.
- Behavior clarifications (argument interpretation, enumerated values, indexing conventions) in the modifier clause.
- Option interactions stated explicitly when behavior depends on another option; use "requires" for mandatory
  companions.
- Mutually exclusive options use parallel phrasing and structure.
- Standalone clarity — understandable without reading surrounding documentation.
- Literals vs. symbolic defaults — single quotes for printed characters; angle brackets for non-printing or symbolic
  values.

**Option ordering**

- Core behavior options first, display options near the bottom, encoding and meta options last.
- Dependent options placed immediately after their parent option.
- Mutually exclusive options grouped together.

**argparse conventions**

- Headings use argparse's default lowercase style.
- Auto-generated options (`-h`/`--help`, `--version`) evaluated only for presence, naming, and placement — not wording.

---

## Mode: Generate

When the user asks to write or generate help text, produce descriptions for each option or the program description as
requested. Apply all rubric standards. Present the proposed text — do not write changes to disk without confirmation
unless the user has asked for direct application.

---

## Output Format

### Review mode

List findings in option-declaration order. For each finding:

- Identify the option or component.
- State the violation precisely, citing the relevant rubric rule.
- Provide the corrected text inline.

End with a summary table:

| Component | Issue | Corrected Text |
|-----------|-------|----------------|

Only include rows for genuine issues. Do not pad with non-issues.

### Generate mode

Present each proposed description with its option name and the proposed text. Wait for confirmation before writing to
disk unless the user has asked for direct application.
