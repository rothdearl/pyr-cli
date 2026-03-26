---
name: changelog
description: Generate a commit message and changelog entry for staged or described changes. Use when asked to write a commit message, changelog entry, or both.
---

This skill is activated when the user describes a set of changes, or asks for a commit message, a changelog entry, or
both. If no changes are described, run `git diff --staged` to inspect what is staged before proceeding.

---

## Commit Messages

### Style

Match the project's established commit message style: a single plain English sentence, no subject prefix or scope tag,
no bullet points. Past tense is acceptable; present tense is also fine — match whichever reads more naturally for the
change.

- `Renamed process_text_stream to process_input_file in the module text_program.`
- `Improved type hinting in the io and render modules.`
- `Removed put_file from the client module since it was just a redundant facade.`

### Rules

- One sentence. No period at the end is fine; a period is also fine — be consistent with the staged changes' context.
- Name the module, class, or function when the change is localized; stay general when the change spans several files.
- Describe what changed, not why — the changelog entry carries the reasoning.
- Do not use conventional commit prefixes (`feat:`, `fix:`, `chore:`), scope tags, or emoji.
- Do not pad a trivial change with inflated language. If a change is minor, say so plainly.

---

## Changelog Entries

Changelog entries accumulate in `CHANGELOG.md` under the `## Unreleased` section. They are short records of individual
changes that feed into release notes — they are not release notes themselves. Each entry covers one logical change.

### Format

```
<module or component>: <what changed and why, in one sentence>.
```

- `io`: Renamed `read_text_files` to `open_text_files` to better reflect that the function returns open file handles
  rather than file contents.
- `render`: Removed the `style_pattern_matches` alias — `style_matches` is now the only public name.
- `cli_program`: Tightened the `initialize_runtime_state` docstring to describe the guarantee rather than the
  implementation.

### Rules

- Lead with the short module name (e.g., `io`, `render`, `text_program`), or a component label (`docs`, `types`,
  `rubric`) for non-code changes.
- One entry per logical change. If a single commit touches three modules independently, produce three entries.
- Include the reason when it is non-obvious or when a caller might need to update their code.
- Omit the reason for purely mechanical changes (formatting, comment rewording, trivial renaming).
- Do not duplicate information already clear from the module name and changed symbol.

---

## Output Format

Present the commit message and changelog entries separately and clearly labeled. If only one was requested, produce only
that.

**Commit message:**

```
<single sentence>
```

**Changelog entries:**

```
<module>: <entry>.
<module>: <entry>.
```

After presenting the entries, append them to the `## Unreleased` section of `CHANGELOG.md`. Insert each entry as a new
bullet at the bottom of the existing list. Do not rewrite or reformat existing entries.

If the changes are ambiguous, ask one focused question before generating — do not guess at intent.
