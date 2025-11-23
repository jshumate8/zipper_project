# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- 

## [0.1.1] - 2025-11-22
### Added
- `--force`/`-f` to allow overwriting an existing output archive.
- `--version` to print package version.
- `--quiet`/`-q` to suppress progress and non-error output.
- Implied recursion for directory inputs (can be disabled with `-R/--no-implied-recurse`).
- Packaging metadata and console script via `pyproject.toml` (`zipper` entry point).
- `CHANGELOG.md` and release notes.

### Changed
- Bumped package version to `0.1.1` and included `LICENSE` file in package metadata.

## [0.1.0] - (initial)
- Initial project skeleton with core zipping functionality, CLI, and basic GUI.
