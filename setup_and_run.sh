#!/usr/bin/env bash
# ==============================================================================
# Coreteron YouTube View Automation Suite - Autonomous End-to-End Setup & Runner
# Supports macOS and all standard Linux distributions (Ubuntu, Debian, Fedora, CentOS, Arch)
# Zero technical expertise, signup, or login required.
# ==============================================================================

set -e

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================================="
echo "    CORETERON YOUTUBE VIEW SUITE - AUTONOMOUS INSTALLER & LAUNCHER"
echo "=================================================================="
echo "Working directory: $SCRIPT_DIR"

# 1. Detect Operating System
OS_TYPE="$(uname -s)"
echo "[+] Detected Platform: $OS_TYPE"

# 2. Verify / Auto-Install Python 3
PYTHON_BIN=""
if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null && python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_BIN="python"
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "[!] Python 3 was not found. Attempting automatic system package installation..."
    if [ "$OS_TYPE" = "Linux" ]; then
        if command -v apt-get &>/dev/null; then
            echo "[+] Installing python3, python3-pip, and python3-venv via apt..."
            sudo apt-get update -y && sudo apt-get install -y python3 python3-pip python3-venv
            PYTHON_BIN="python3"
        elif command -v dnf &>/dev/null; then
            echo "[+] Installing python3, python3-pip via dnf..."
            sudo dnf install -y python3 python3-pip
            PYTHON_BIN="python3"
        elif command -v pacman &>/dev/null; then
            echo "[+] Installing python, python-pip via pacman..."
            sudo pacman -Sy --noconfirm python python-pip
            PYTHON_BIN="python3"
        else
            echo "[-] Error: Package manager not recognized. Please install Python 3.9+ manually."
            exit 1
        fi
    elif [ "$OS_TYPE" = "Darwin" ]; then
        if command -v brew &>/dev/null; then
            echo "[+] Installing python via Homebrew..."
            brew install python
            PYTHON_BIN="python3"
        else
            echo "[-] Error: Python 3 not found on macOS. Please install it from https://www.python.org/downloads/ or run 'xcode-select --install'."
            exit 1
        fi
    fi
fi

echo "[+] Python Interpreter: $($PYTHON_BIN --version)"

# 3. Create Virtual Environment
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Initializing dedicated isolated environment (.venv)..."
    $PYTHON_BIN -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

# 4. Upgrade pip and install wheel/setuptools
echo "[+] Upgrading pip and core build tools..."
"$VENV_PIP" install -q --upgrade pip setuptools wheel

# 5. Install Required Python Packages
echo "[+] Installing project requirements from requirements.txt..."
"$VENV_PIP" install -q -r "$SCRIPT_DIR/requirements.txt"

# 6. Install Playwright Chromium Browser and OS Dependencies
echo "[+] Installing Playwright Chromium browser binary..."
if [ "$OS_TYPE" = "Linux" ]; then
    echo "[+] Ensuring Linux browser libraries are present..."
    "$VENV_PYTHON" -m playwright install --with-deps chromium || "$VENV_PYTHON" -m playwright install chromium
else
    "$VENV_PYTHON" -m playwright install chromium
fi

# 7. Ensure .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        echo "[+] Setting default configuration from .env.example..."
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    fi
fi

# 8. Launch Web Dashboard and Open Browser
PORT=5055
URL="http://127.0.0.1:$PORT"

echo "=================================================================="
echo "[+] Starting Coreteron YouTube View Suite at $URL ..."
echo "[+] Opening dashboard in your default browser..."
echo "=================================================================="

# Background process to open browser
(
    sleep 2
    if [ "$OS_TYPE" = "Darwin" ]; then
        open "$URL" 2>/dev/null || true
    elif [ "$OS_TYPE" = "Linux" ]; then
        xdg-open "$URL" 2>/dev/null || true
    fi
) &

# Run Flask application
exec "$VENV_PYTHON" "$SCRIPT_DIR/app.py"
