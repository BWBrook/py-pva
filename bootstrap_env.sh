#!/bin/bash
# Create and configure the Python virtual environment for the PVA simulator.
# This script uses python3 if python3.12 is unavailable. It installs
# dependencies from requirements.txt via `uv pip` and freezes them into
# requirements.lock using `uv pip freeze`.

PYTHON_BIN="python3.12"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
uv pip install -r requirements.txt
uv pip freeze > requirements.lock

echo "Virtual environment created using $PYTHON_BIN."
