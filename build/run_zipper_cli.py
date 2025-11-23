import sys
from pathlib import Path

# Add parent directory to path so zipper module can be found
sys.path.insert(0, str(Path(__file__).parent.parent))

from zipper.cli import main

if __name__ == "__main__":
    main()
