#!/usr/bin/env python3
"""Interactive 1-Click Showcase Demo for Coreteron YouTube View Automation.

Designed for executive demonstration and technical review with Coreteron team.
Demonstrates:
- Autonomous proxy rotation & stealth browser setup
- 144p dynamic bandwidth throttling to optimize residential proxy budgets
- Human-like viewer engagement (mouse trajectories, comment scrolling)
- YouTube telemetry verification and CSV logging
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import os
from pathlib import Path
import sys
import time

from config import BotConfig
from proxy_manager import ProxyManager
from session_tracker import SessionTracker
from view_worker import run_single_view

BASE_DIR = Path(__file__).resolve().parent


def print_banner():
    print("""
========================================================================
     CORETERON AUTOMATION LABS - YOUTUBE VIEW ENGINE DEMO
========================================================================
Architecture:
- Playwright Chromium with Anti-Fingerprinting & Stealth Hooks
- Residential / Rotating Proxy Gateway Integration
- Dynamic Quality Throttling to 144p (Saves ~88% Bandwidth)
- Multi-Worker Concurrency with Telemetry Validation
========================================================================
""")


async def run_showcase_demo():
    print_banner()

    default_url = "https://www.youtube.com/watch?v=DwRt5d-3AWc"
    print(f"Target Video URL: {default_url} ('She Was Rejected. So She Built Her Own Salon Empire!')")
    print("Mode: Live Visual Browser Demo (Headed Mode enabled for showcase)")
    print("Demo Scope: 2 Consecutive Automated Sessions with Proxy Rotation\n")

    cfg = BotConfig()
    cfg.target_url = default_url
    cfg.headless = False  # Visible browser for showcase
    cfg.min_watch_seconds = 32  # Meet YouTube 30s threshold
    cfg.max_watch_seconds = 40
    cfg.target_views = 2

    proxy_mgr = ProxyManager(proxy_file=cfg.proxy_file, rotating_gateway=cfg.rotating_gateway)
    tracker = SessionTracker()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Initialized Proxy Manager ({proxy_mgr.total_proxies} configured proxies)")
    if proxy_mgr.total_proxies == 0:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Note: No proxies in proxies.txt. Running demo via direct connection with simulated proxy rotation.")

    for i in range(1, cfg.target_views + 1):
        session_id = f"DEMO-{i:02d}"
        proxy = proxy_mgr.get_proxy(rotate=True)
        proxy_desc = proxy.get("server") if proxy else "Local Interface (Simulated Residential Pool)"

        print("\n" + "-" * 60)
        print(f"STAGE {i}/{cfg.target_views}: Initiating Autonomous View Session [{session_id}]")
        print(f"Proxy Node:         {proxy_desc}")
        print(f"Fingerprint Shield: Enabled (navigator.webdriver stripped, WebGL spoofed)")
        print(f"Bandwidth Strategy: 144p Forced Stream (~0.3 MB per view)")
        print("-" * 60)

        success = await run_single_view(
            session_id=session_id,
            target_url=cfg.target_url,
            proxy_config=proxy,
            watch_seconds=35,
            headless=False,
            tracker=tracker,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport=(1366, 768),
            force_144p=True,
            mute_audio=True,
        )

        status_text = "VERIFIED (Exceeded 30s playback threshold)" if success else "INCOMPLETE"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Session {session_id} Status: {status_text}")
        await asyncio.sleep(2)

    summary = tracker.get_summary()
    print("\n" + "=" * 70)
    print("DEMONSTRATION RESULTS")
    print("=" * 70)
    print(f"Sessions Attempted:     {summary['total']}")
    print(f"Sessions Validated:     {summary['successful']}")
    print(f"Success Verification:   {summary['rate']}%")
    print(f"Audit Trail CSV:        {tracker.csv_path}")
    print(f"Session Summary JSON:   {tracker.json_path}")
    print("=" * 70)
    print("Demonstration successfully finished.")


if __name__ == "__main__":
    asyncio.run(run_showcase_demo())
