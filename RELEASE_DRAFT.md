# Release Draft: v0.1.1

Release date: 2025-11-22

Summary
-------
This release adds several usability and packaging improvements to `zipper`, including:

- New CLI flags: `--force`, `--version`, and `--quiet`.
- Implied recursion when passing directories (can be disabled with `-R`).
- Improved packaging (`pyproject.toml`) and a `zipper` console script for easy installation.
- A `LICENSE` file and updated metadata to prepare for distribution.

Release notes
------------
(See `RELEASE_NOTES.md` and `CHANGELOG.md` for full details.)

Tag
---
Proposed tag: `v0.1.1`

Actions (suggested)
-------------------
- Review and commit these changes locally.
- Create the annotated git tag locally:
  ```powershell
  git tag -a v0.1.1 -m "Release v0.1.1"
  ```
- Push the tag to the remote (GitHub):
  ```powershell
  git push origin v0.1.1
  ```
- Create a GitHub Release using tag `v0.1.1` and paste the contents of `RELEASE_NOTES.md` as the release body.

Helper scripts
--------------
You can use the helper scripts in `scripts/` to create and push the release:

PowerShell (recommended on Windows):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\release.ps1 -Tag v0.1.1 -Message "Release v0.1.1" -Push -CreateGhRelease
```

POSIX shell (macOS / Linux):

```bash
./scripts/release.sh v0.1.1 "Release v0.1.1" --push --gh
```

Both scripts perform safety checks (git available, clean working tree unless you opt out) and will only push/create a GitHub release if you pass the relevant flags.

Notes
-----
I created this draft file and helper scripts in the repo. I did not push any tags or changes to a remote. If you'd like, I can push the tag and create a GitHub release (requires network access and proper remote configuration/credentials).
