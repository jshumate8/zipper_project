#!/usr/bin/env bash
# Create and populate a Python virtual environment for development (POSIX)
# Usage: ./scripts/dev_setup.sh [--with-optional]

set -euo pipefail

VENV_DIR=".venv"
PYTHON=${PYTHON:-python}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python is not available on PATH. Install Python 3.8+ and try again." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv at $VENV_DIR..."
  "$PYTHON" -m venv "$VENV_DIR"
else
  echo "$VENV_DIR already exists — reusing it."
fi

VENV_PY="$VENV_DIR/bin/python"
"$VENV_PY" -m pip install --upgrade pip setuptools wheel
"$VENV_PY" -m pip install pytest

if [ "${1:-}" = "--with-optional" ]; then
  if [ -f requirements.txt ]; then
    echo "Installing optional requirements..."
    "$VENV_PY" -m pip install -r requirements.txt
  else
    echo "requirements.txt not found — skipping optional install"
  fi
fi

echo "Done. Activate with: source .venv/bin/activate"
echo "Run tests: python -m pytest -q"
