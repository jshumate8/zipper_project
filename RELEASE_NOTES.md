Release notes for `zipper` v0.1.1

Release date: 2025-11-22

Summary
-------
This release adds several usability and packaging improvements to `zipper`, including:

- New CLI flags: `--force`, `--version`, and `--quiet`.
- Implied recursion when passing directories (can be disabled with `-R`).
- Improved packaging (`pyproject.toml`) and a `zipper` console script for easy installation.
- A `LICENSE` file and updated metadata to prepare for distribution.
- Tests and CI workflow added (GitHub Actions) to be created in project root.

Developer notes
---------------
- Packaging: Version bumped to `0.1.1`.
- Optional dependencies: `pyzipper` for AES encryption, `tqdm` for progress bar, `tkinterdnd2` for drag-and-drop.

Upgrade instructions
--------------------
To install the new version locally (editable):

```powershell
python -m pip install -e .
```

To build a wheel and source distribution:

```powershell
python -m pip install build
python -m build
```

If publishing, use `twine` to upload artifacts in `dist/`.

Notes for maintainers
---------------------
- Consider adding a `dev` extras group in `pyproject.toml` with `pytest` and linters.
- Consider tagging the release in git (e.g., `git tag v0.1.1`) and creating a GitHub release with these notes.
