# Coreteron YouTube View Automation Suite

Autonomous YouTube playback verification suite featuring anti-fingerprinting stealth evasion, rotating residential proxy gateway integration, dynamic 144p DASH bandwidth throttling, and organic human behavior simulation.

---

## Video Demonstration

A complete product walkthrough demonstrating proxy connectivity tests, 144p dynamic stream throttling, real-time telemetry, and verified view counters is included in the repository:
- Video File: [demo/CORETERON_YOUTUBE_SUITE_DEMO.mp4](demo/CORETERON_YOUTUBE_SUITE_DEMO.mp4) (720p HD, 53s, 3.6 MB)

---

## 1-Click Autonomous Setup (Zero Technical Expertise)

No manual Python configuration, environment activation, or package commands are required. The automated setup script detects your operating system, configures Python, creates the isolated virtual environment, installs all dependencies and browser binaries, and opens the Web Dashboard in your default browser.

### Windows
- Double-click **`setup_and_run.bat`** (or `Start_Windows.bat`).
- If Python is not installed, the script will automatically download and install Python 3.11 with PATH enabled.

### macOS
- Double-click **`Start_Mac.command`** or open Terminal and run:
  ```bash
  ./setup_and_run.sh
  ```

### Linux (Ubuntu, Debian, Fedora, Arch)
- Open Terminal in the repository folder and run:
  ```bash
  ./setup_and_run.sh
  ```

---

## Manual Developer Setup (Optional)

### Step 1: Clone Repository
```bash
git clone https://github.com/coder-irwin/coreteron-yt-bot.git
cd coreteron-yt-bot
```

### Step 2: Configure Environment (.env)
Create a `.env` file in the project root directory or copy `.env.example`:
```bash
cp .env.example .env
```

If creating manually, paste the following configuration:
```env
PORT=5055
TARGET_URL=https://youtu.be/DwRt5d-3AWc?si=8up-r-mjItwVYKMf
PROXY_GATEWAY=http://olqlayvv-rotate:a1ahaeqjq3df@p.webshare.io:80
TARGET_VIEWS=5
CONCURRENCY=2
MIN_WATCH_SECONDS=35
MAX_WATCH_SECONDS=65
FORCE_144P=true
HEADLESS=false
```

### Step 3: Install Dependencies and Launch

#### Option A: 1-Click Launchers
- **macOS**: Double-click `Start_Mac.command` (or run `./setup_and_run.sh`).
- **Linux**: Run `./setup_and_run.sh`.
- **Windows**: Double-click `setup_and_run.bat`.

#### Option B: Terminal Setup by Operating System

**macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python app.py
```

**Linux (Ubuntu / Debian / RHEL):**
```bash
# On Ubuntu/Debian ensure Python venv is installed:
# sudo apt update && sudo apt install -y python3-venv python3-pip

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python app.py
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt
playwright install chromium
python app.py
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
python app.py
```

The Web Dashboard opens automatically at:
```
http://127.0.0.1:5055
```

---

## Command Line Interface (CLI)

You can also run view campaigns directly without the web browser interface:

```bash
# Standard run (5 views, visible browser for live verification)
python runner.py --url "https://youtu.be/DwRt5d-3AWc?si=8up-r-mjItwVYKMf" --views 5

# Production scale (100 views, 5 concurrent headless workers)
python runner.py \
  --url "https://youtu.be/DwRt5d-3AWc?si=8up-r-mjItwVYKMf" \
  --views 100 \
  --concurrency 5 \
  --headless \
  --min-watch 35 \
  --max-watch 70 \
  --gateway "http://olqlayvv-rotate:a1ahaeqjq3df@p.webshare.io:80"
```

---

## Capabilities & Architecture

- **Rotating Residential Proxy Integration**: Direct backconnect proxy routing via Webshare, Smartproxy, Bright Data, or custom SOCKS5 gateways.
- **Dynamic 144p Bandwidth Throttling**: Enforces lowest-resolution DASH video streaming via HTML5 player hooks, saving ~88% of residential proxy data (~0.3 MB per view vs ~2.5 MB on 720p).
- **Stealth Anti-Detection Shield**: Strips `navigator.webdriver`, spoofs realistic WebGL NVIDIA/Apple hardware profiles, and randomizes viewport dimensions.
- **Organic Human Emulation**: Bezier mouse movement curves, natural comment section scrolling, and variable watch time curves.
- **Audit Trails & Telemetry**: Full session verification logging to CSV and JSON formats.

---

## Bandwidth & Cost Modeling (10,000 Views)

| Strategy | Resolution | Avg Data / View | Total Data (10,000 Views) | Est. Cost ($2.50/GB) |
|---|---|---|---|---|
| Standard Bot | 720p / Auto | ~2.5 MB | 25.0 GB | $62.50 |
| **Coreteron Suite** | **144p (Tiny)** | **~0.3 MB** | **3.0 GB** | **$7.50** |

Enforcing 144p stream parameters reduces operational proxy expenditure by over 88% at scale.

---

## Project Structure

```
coreteron_yt_bot/
|-- app.py                 # Real-time web dashboard server and SSE telemetry
|-- config.py              # Configuration dataclass and defaults
|-- proxy_manager.py       # Rotating proxy gateway connectivity and diagnostics
|-- stealth_context.py     # Anti-fingerprint and navigator.webdriver evasion
|-- player_controller.py   # Consent dismissal, 144p quality enforcement, playback checks
|-- behavior_engine.py     # Bezier mouse curves and organic scroll engine
|-- session_tracker.py     # Thread-safe CSV/JSON audit logging
|-- view_worker.py         # Autonomous single-view session executor
|-- runner.py              # Concurrency manager and CLI entry point
|-- run_demo.py            # Automated verification test script
|-- proxies.txt            # Optional proxy list file
|-- demo/                  # Product video demonstration (MP4)
|-- templates/index.html   # Web dashboard user interface
|-- static/                # Dashboard stylesheets and client script
|-- Start_Mac.command      # 1-Click macOS launcher script
|-- Start_Linux.sh         # 1-Click Linux launcher script
|-- Start_Windows.bat      # 1-Click Windows launcher script
|-- requirements.txt       # Python dependencies
|-- .env.example           # Environment variables template
|-- .gitignore             # Git ignore rules
`-- README.md              # Operations guide
```
