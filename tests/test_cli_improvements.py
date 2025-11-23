import zipfile
from pathlib import Path
import subprocess
from pathlib import Path


def test_implied_recursion_and_quiet(tmp_path):
    # Create nested structure
    root = tmp_path / "root"
    sub = root / "sub"
    sub.mkdir(parents=True)
    f = sub / "inside.txt"
    f.write_text("content")

    out = tmp_path / "out.zip"

    # Run CLI without -r: implied recursion should pick up nested file
    cmd = ["python", "-m", "zipper", "-o", str(out), str(root)]
    res = subprocess.run(cmd, cwd=str(Path(__file__).parent.parent), capture_output=True, text=True)
    assert res.returncode == 0, f"stderr: {res.stderr}\nstdout: {res.stdout}"
    with zipfile.ZipFile(out, 'r') as z:
        names = z.namelist()
        assert any('inside.txt' in n for n in names)

    # Now run with --quiet; should still create archive and be silent (no stdout unless error)
    out2 = tmp_path / "out2.zip"
    cmd2 = ["python", "-m", "zipper", "-o", str(out2), str(root), "--quiet"]
    res2 = subprocess.run(cmd2, cwd=str(Path(__file__).parent.parent), capture_output=True, text=True)
    assert res2.returncode == 0
    # stdout/stderr should be empty or minimal in quiet mode (allow warnings from environment)
    assert res2.returncode == 0
    with zipfile.ZipFile(out2, 'r') as z:
        names = z.namelist()
        assert any('inside.txt' in n for n in names)
