# Changelog

All notable changes to this project are documented here. Entries accumulate under **Unreleased** and are promoted to a
versioned section when a release is cut.

---

## Unreleased

- `env`: Improved docstrings for `get_env_str` and `get_required_env_str` to more accurately describe trim behavior.
- `docs`: Updated multi-line docstrings across `pyrcli.cli` and `pyrcli.cli.progress` to conform to PEP 257 — summary line now starts on the same line as the opening `"""`.
- `client`: Removed redundant `accept` default documentation from `delete`, `get`, `post`, and `put`; simplified `set_timeout` docstring.
- `config`: Added `.claude/settings.json` to configure Claude Code tool permissions for the project.
- `config`: Added `git diff --staged` allow rules to `.claude/settings.json` to suppress permission prompts from the changelog skill.
- `rubric`: Simplified the title of `code_evaluation_rubric.md` from "Python Code Evaluation Rubric and Design Guidelines" to "Python Code Evaluation Rubric".
- `render`: Changed `#:` comment on `_MatchRange` to `#` — Sphinx-style attribute docs have no effect on private symbols.
- `dupe`: Changed `#:` comment on `_LineGroups` to `#` — Sphinx-style attribute docs have no effect on private symbols.
- `order`: Changed `#:` comments on `_DateSortSegment` and `_NumericSortSegment` to `#` — Sphinx-style attribute docs have no effect on private symbols.
- `CLAUDE.md`: Revised import policy to follow the Google Python Style Guide — utility modules imported as modules; classes, type aliases, and constants imported by name.
- `rubric`: Revised import policy section to distinguish utility module imports from direct name imports for types and constants, with a usage-based evaluator heuristic.
- `__about__`: Updated `_get_version` docstring to document the ``"0+unknown"`` fallback when the package is not installed.
- `emit`: Fixed `--stdin-after` description ("read from standard input" replacing "process standard input") and moved `--no-newline` after the processing options.
- `glue`: Clarified `--number` as "number all lines", `--no-blank` as "suppress all blank lines", and added missing article to `--show-ends` description.
- `num`: Clarified `--no-blank` as "suppress all blank lines".
- `order`: Clarified `--no-blank` as "suppress all blank lines".
- `scan`: Fixed `--stdin-files` description to match project convention ("read FILES from standard input (one per line)").
- `seek`: Updated epilog to match project convention ("search the current directory when no DIRECTORIES are specified").
- `show`: Clarified `--line-numbers` as "number all lines".

---

## 1.4.10 — 2026-03-27

- `skills`: Added the `audit-docs` skill for verifying that README.md and CLAUDE.md are consistent with the project.
- `skills`: Added the `docstring` skill for reviewing and generating docstrings in isolation.
- `skills`: Added the `evaluate` skill for evaluating modules against the project's coding standards.
- `skills`: Added the `help-text` skill for evaluating and generating argparse help text against the help text rubric.
- `skills`: Added the `release-docs` skill for generating structured release notes at release time.
- `skills`: Added the `type-hints` skill for reviewing type annotation usage against the project's rubric.
- `CLAUDE.md`: Updated references to correctly point to the rubric files in `docs/`.
- `docs`: Reformatted `code_evaluation_rubric.md` to be faithful to the original rubric content.
- `skills`: Added the `changelog` skill for generating commit messages and changelog entries from staged changes.
- `skills`: Renamed the `type-hints` skill to `typing` to better align with Python's own vocabulary for the domain.
- `skills`: Updated the `changelog` skill to append entries to CHANGELOG.md under the Unreleased section.
- `skills`: Updated the `release-docs` skill to read from CHANGELOG.md and reset the Unreleased section after a release.
- `docs`: Added CHANGELOG.md with the unreleased accumulation structure, seeded with entries from the current cycle.
- `CLAUDE.md`: Added a note to the Versioning section documenting the CHANGELOG.md unreleased accumulation workflow.
- `show`: Changed `Sequence[str]` to `Collection[str]` in `get_line_range` and `print_lines` — neither method uses indexing or ordering, only `len()` and iteration.
- `track`: Changed `Sequence[str]` to `Collection[str]` in `print_lines` — the method uses only `len()` and iteration.
- `dupe`: Changed `Sequence[str]` to `Collection[str]` in the inner type of `print_line_groups` — each group is accessed only via `len()` and iteration.
- `types`: Changed `CompiledPatterns` from `Sequence[re.Pattern[str]]` to `Collection[re.Pattern[str]]` — callers use only boolean checks and iteration, not indexing or ordering.
- `text_program`: Changed `post_execute` parameter from `Sequence[str]` to `Collection[str]` — overrides require only `len()` and iteration.
- `docs`: Updated `post_execute` signature in README.md to reflect the type change.
- `docs`: Corrected the `pyrcli.cli.http` module listing in README.md — renamed `responses` to `json`.
- `docs`: Corrected the `initialize_runtime_state` section in README.md — renamed `print_color` to `use_color`.
- `env`: Added `get_env_str` and `get_required_env_str` for reading environment variables with optional whitespace trimming.
- `tests`: Added `test_env.py` with full coverage of the env module.
