#!/bin/bash
# ==============================================================================
# Coreteron YouTube View Automation Suite - Autonomous 1-Click Launcher (macOS)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================================"
echo "    Coreteron YouTube View Automation Suite - Web Dashboard"
echo "========================================================================"
echo "Working directory: $SCRIPT_DIR"

# Locate Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 was not found on this system."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Python interpreter: $($PYTHON_CMD --version)"

# Check / create virtual environment
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    if [ -d "$SCRIPT_DIR/../.venv" ]; then
        VENV_DIR="$SCRIPT_DIR/../.venv"
        echo "Using existing workspace virtual environment: $VENV_DIR"
    else
        echo "Creating virtual environment at $VENV_DIR..."
        $PYTHON_CMD -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
        echo "Installing requirements..."
        pip install --upgrade pip
        pip install -r requirements.txt
        playwright install chromium
    fi
fi

source "$VENV_DIR/bin/activate"

# Automatically open default browser after server initializes
(sleep 2 && open "http://127.0.0.1:5055") &

# Start Web Application Dashboard
python "$SCRIPT_DIR/app.py"
