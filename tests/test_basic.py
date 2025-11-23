import tempfile
import shutil
import os
import zipfile
from pathlib import Path
import subprocess


def test_zip_simple(tmp_path):
    # create some files and a dir
    d = tmp_path / "mydir"
    d.mkdir()
    f1 = tmp_path / "a.txt"
    f1.write_text("hello")
    f2 = d / "b.txt"
    f2.write_text("world")

    out = tmp_path / "out.zip"

    # run the CLI module
    cmd = ["python", "-m", "zipper", "-o", str(out), str(f1), str(d)]
    res = subprocess.run(cmd, cwd=str(Path(__file__).parent.parent), capture_output=True, text=True)
    assert res.returncode == 0, f"stderr: {res.stderr}\nstdout: {res.stdout}"

    # verify zip contents
    with zipfile.ZipFile(out, 'r') as z:
        names = z.namelist()
        assert any('a.txt' in n for n in names)
        assert any('mydir' in n and 'b.txt' in n for n in names)
