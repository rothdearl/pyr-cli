# Changelog

All notable changes to this project are documented here. Entries accumulate under **Unreleased** and are promoted to a
versioned section when a release is cut.

---

## Unreleased

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
