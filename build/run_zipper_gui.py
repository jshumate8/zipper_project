import sys
from pathlib import Path

# Add parent directory to path so zipper module can be found
sys.path.insert(0, str(Path(__file__).parent.parent))

from zipper.gui import run_gui

if __name__ == "__main__":
    run_gui()
