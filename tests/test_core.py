import zipfile
from pathlib import Path

from zipper.core import collect_files, create_zip


def test_collect_files_and_create_zip(tmp_path):
    # Setup files and directories
    d = tmp_path / "mydir"
    d.mkdir()
    f1 = tmp_path / "a.txt"
    f1.write_text("hello")
    f2 = d / "b.txt"
    f2.write_text("world")
    hidden = d / ".secret"
    hidden.write_text("sensitive")

    # Collect without recursion (directory input should include its immediate files)
    files = collect_files([str(f1), str(d)], recurse=False, exclude_patterns=[], include_hidden=False)
    names = {str(rel) for (_, rel) in files}
    assert any('a.txt' in n for n in names)
    assert any('mydir' in n and 'b.txt' in n for n in names)
    # hidden file should be excluded
    assert not any('.secret' in n for n in names)

    # Test exclude patterns: exclude only .txt files, hidden should be included
    files_excluded = collect_files([str(f1), str(d)], recurse=True, exclude_patterns=['*.txt'], include_hidden=True)
    # No .txt files should remain
    assert all(not str(rel).endswith('.txt') for (_, rel) in files_excluded)
    # Hidden file should be present when include_hidden=True
    assert any('.secret' in str(rel) for (_, rel) in files_excluded)

    # Create zip and verify contents and progress callback
    out = tmp_path / "out.zip"
    progress_calls = []

    def progress_cb(total, done, current):
        progress_calls.append((total, done, str(current)))

    # Re-collect with recursion to include files inside dirs
    files = collect_files([str(f1), str(d)], recurse=True, exclude_patterns=[], include_hidden=False)
    create_zip(str(out), files, compresslevel=6, verbose=False, password=None, progress_callback=progress_cb)

    assert out.exists()
    with zipfile.ZipFile(out, 'r') as z:
        names = z.namelist()
        assert any('a.txt' in n for n in names)
        assert any('mydir' in n and 'b.txt' in n for n in names)

    # Progress callback should have been called at least once
    assert progress_calls, "progress_callback was not called"
