import zipfile
from pathlib import Path
import subprocess


def test_force_overwrite(tmp_path):
    # Create initial zip file to be overwritten
    out = tmp_path / "out.zip"
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr('old.txt', 'old')
    size_before = out.stat().st_size

    # Create files to zip
    d = tmp_path / 'data'
    d.mkdir()
    f = d / 'new.txt'
    f.write_text('new')

    # Run CLI without --force; should fail (return code 4) and not overwrite
    cmd = ["python", "-m", "zipper", "-o", str(out), str(d)]
    res = subprocess.run(cmd, cwd=str(Path(__file__).parent.parent), capture_output=True, text=True)
    assert res.returncode == 4
    assert out.exists()
    assert out.stat().st_size == size_before

    # Run CLI with --force; should succeed and overwrite archive
    cmd2 = ["python", "-m", "zipper", "-o", str(out), str(d), "--force"]
    res2 = subprocess.run(cmd2, cwd=str(Path(__file__).parent.parent), capture_output=True, text=True)
    assert res2.returncode == 0
    assert out.exists()
    with zipfile.ZipFile(out, 'r') as z:
        names = z.namelist()
        assert any('new.txt' in n for n in names)
