#!/bin/bash
# ==============================================================================
# Coreteron YouTube View Automation Suite - 1-Click Linux Launcher
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=================================================================="
echo "    [+] STARTING CORETERON YOUTUBE VIEW SUITE (Linux)             "
echo "=================================================================="

if ! command -v python3 &> /dev/null; then
    echo ""
    echo "[-] Python 3 is not detected on your system."
    echo "[!] On Ubuntu/Debian: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
    echo "[!] On Fedora/RHEL:   sudo dnf install -y python3 python3-pip"
    echo ""
    exit 1
fi

echo "[+] Python detected: $(python3 --version)"

if [ ! -d ".venv" ]; then
    echo "[+] Initializing isolated environment (.venv)..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "[+] Verifying package dependencies..."
python3 -m pip install -q --upgrade pip
python3 -m pip install -q -r requirements.txt

echo "[+] Verifying Playwright browser..."
python3 -m playwright install chromium

echo "=================================================================="
echo "[+] Starting Web Dashboard at http://127.0.0.1:5055 ..."
echo "=================================================================="

if command -v xdg-open &> /dev/null; then
    (sleep 2 && xdg-open "http://127.0.0.1:5055") &
fi

python3 app.py
