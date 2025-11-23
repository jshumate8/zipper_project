import subprocess
from pathlib import Path
from zipper import __version__


def test_cli_version_flag():
    cmd = ["python", "-m", "zipper", "--version"]
    res = subprocess.run(cmd, cwd=str(Path(__file__).parent.parent), capture_output=True, text=True)
    assert res.returncode == 0
    # argparse's version action prints the version and newline
    assert __version__ in res.stdout.strip()
