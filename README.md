# Zipper

A small, dependency-light Python CLI and simple GUI to create zip archives from files and directories.

## 🚀 Windows Users: Quick Start

**No Python installation required!** Download the pre-built executables from the [latest release](https://github.com/jshumate8/zipper_project/releases/latest):

- **`zipper-gui.exe`** - Double-click to launch the graphical interface
- **`zipper-cli.exe`** - Command-line tool (use in PowerShell/CMD)

After downloading, you can run immediately:
```powershell
# GUI: Just double-click zipper-gui.exe
# CLI: Use in terminal
.\zipper-cli.exe --help
.\zipper-cli.exe -o archive.zip myfiles\

**Features**
- Add files and directories to an archive
- Implied recursion for directory inputs (can be disabled)
- Explicit recursion (`-r`) and opt-out `-R/--no-implied-recurse`
- Compression level (`-l 0..9`)
- Exclude glob patterns (`-e`) and option to include hidden files
- Verbose (`-v`) and quiet (`-q`) modes
- Overwrite protection with `--force` to allow replacing existing outputs
- Optional AES encryption via `pyzipper` when `--encrypt` is used

**Quick Usage (PowerShell)**

Create `archive.zip` from `file.txt` and `mydir` (implied recursion will include nested files):

```powershell
python -m zipper -o archive.zip file.txt mydir
```

Create recursively with level 9 compression and verbose output:

```powershell
python -m zipper -o archive.zip -r -l 9 -v mydir
```

Exclude `*.log` files:

```powershell
python -m zipper -o archive.zip -r -e "*.log" mydir
```

Show version:

```powershell
python -m zipper --version
```

Run quietly (no progress or verbose output):

```powershell
python -m zipper -o archive.zip -r --quiet mydir
```

Force overwrite an existing output file:

```powershell
python -m zipper -o archive.zip -r --force mydir
```

Run tests (requires `pytest`):

```powershell
python -m pip install pytest
pytest -q
```

**GUI**

Start the Tkinter GUI:

```powershell
python -c "import zipper.gui; zipper.gui.run_gui()"
```

**Optional dependencies**
- `tqdm` — shows a progress bar in the terminal when present
- `pyzipper` — enables AES encryption when using `--encrypt`
- `tkinterdnd2` — improves drag-and-drop support for the Tk GUI on some platforms

Install optional extras (one-off):

```powershell
python -m pip install tqdm pyzipper tkinterdnd2
```

Notes
- The CLI will refuse to overwrite an existing output file unless `--force` is passed (exit code `4`).
- By default, if you pass a directory as an input the CLI will include its contents recursively; use `-R/--no-implied-recurse` to force no implied recursion.

If you'd like, I can add a `pyproject.toml` and a console-script entry so users can run `zipper` directly after installing the package.

