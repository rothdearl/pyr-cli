---
name: release-docs
description: Generate structured release notes for a Pyr-CLI patch or minor release using the project's established format and conventions.
---

This skill is activated when the user describes a set of changes and asks for release notes, release documentation, or a
release summary. Generate release notes based on the changes provided. Output must follow the established format and
tone used throughout the project's release history.

---

## Release Notes Format

Always produce release notes using this exact structure. Every section must be present, even if its content is "None.":

```markdown
## Overview

<One or two sentences summarizing the nature and scope of the release.>

---

## Highlights

<Bullet list of the most significant user-facing changes. Omit if there are no notable highlights — do not force
highlights for trivial releases.>

---

## Changes

<Bullet list of public API changes, behavioral changes, and renamed or removed symbols. Use the format:>

- `module`: Description of the change.

---

## Internal Improvements

<Bullet list of internal, non-breaking improvements: private renames, structural refactors, type hint improvements,
comment updates.>

---

## Documentation

<Bullet list of documentation-only changes: docstring revisions, rubric updates, README changes, new or updated markdown
files.>

---

## Compatibility

**Breaking changes:**

<Bullet list of breaking changes with before/after migration guidance. If none, write "None.">
```

---

## Tone and Style

- The overview should be a single concise paragraph — one to two sentences. It names the nature of the release (
  refinement, additive, focused, etc.) without marketing language.
- Highlights should be written as complete sentences, not imperative commands.
- Change bullets should be specific: name the module and the exact symbol or behavior that changed.
- Breaking changes must include enough context for a caller to migrate without reading the source. Provide a code
  example when the migration pattern is non-obvious.
- Do not inflate the release. If a release is trivial, say so in the overview. Do not invent highlights for patch
  releases.

---

## Categorization Rules

Apply these rules when categorizing changes:

| Change type                                            | Section                 |
|--------------------------------------------------------|-------------------------|
| Public API rename (function, class, attribute, module) | Changes + Compatibility |
| Behavioral change visible to callers                   | Changes + Compatibility |
| New public parameter with a default (non-breaking)     | Changes                 |
| Removal of a public symbol                             | Changes + Compatibility |
| Private function or variable rename                    | Internal Improvements   |
| Type hint correction or improvement                    | Internal Improvements   |
| Structural refactor with no API impact                 | Internal Improvements   |
| Docstring or comment revision                          | Documentation           |
| Rubric or markdown file update                         | Documentation           |
| New or converted documentation file                    | Documentation           |

When a change appears in both Changes and Compatibility, it must be listed in both sections — do not consolidate.

---

## Breaking Change Format

For each breaking change, provide:

- The old fully-qualified name and the new fully-qualified name using an arrow: `old` → `new`
- A migration example when the rename affects call sites in a non-obvious way:

``` python
# Before
old_module.old_function(...)

# After
new_module.new_function(...)
```

Only include a code example when the migration requires more than a symbol substitution (e.g., a module rename that
changes the import path, or a parameter rename that affects keyword arguments).

---

## Project Context

This is **Pyr-CLI** — a toolkit of composable Unix-style CLI programs. The project uses a single project-wide version
number. Release notes cover changes to:

- `pyrcli.cli` — the core CLI framework
- `pyrcli.cli.http` — optional HTTP helpers
- `pyrcli.cli.progress` — optional terminal progress indicators
- Command implementations in `pyrcli.commands`

Refer to module names using their short form (e.g., `io`, `render`, `cli_program`) in the Changes section, and their
fully-qualified form (e.g., `http.upload`, `cli.render`) in the Compatibility section when disambiguation is needed.
