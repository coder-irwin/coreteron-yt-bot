#!/usr/bin/env python3
"""Concurrency Runner for Coreteron YouTube View Automation Suite.

Orchestrates multi-worker viewing campaigns, rotates proxies across sessions,
and produces live console metrics.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import logging
from pathlib import Path
import random
import sys
import time
from typing import Optional

from config import BotConfig
from proxy_manager import ProxyManager
from session_tracker import SessionTracker
from view_worker import run_single_view

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("runner")


class CampaignRunner:
    """Manages autonomous view bot campaigns."""

    def __init__(self, config: Optional[BotConfig] = None):
        self.config = config or BotConfig()
        self.proxy_mgr = ProxyManager(
            proxy_file=self.config.proxy_file,
            rotating_gateway=self.config.rotating_gateway,
        )
        self.tracker = SessionTracker()
        self.semaphore = asyncio.Semaphore(self.config.concurrency)

    async def _worker_task(self, index: int, total: int) -> bool:
        session_id = f"WORKER-{index:03d}"
        proxy = self.proxy_mgr.get_proxy(rotate=True)
        watch_time = random.randint(self.config.min_watch_seconds, self.config.max_watch_seconds)
        ua = random.choice(self.config.user_agents)
        vp = random.choice(self.config.viewports) if self.config.randomize_viewport else (1280, 800)

        async with self.semaphore:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Launching Session {index}/{total} on {proxy.get('server', 'Direct') if proxy else 'Direct Connection'}...")
            return await run_single_view(
                session_id=session_id,
                target_url=self.config.target_url,
                proxy_config=proxy,
                watch_seconds=watch_time,
                headless=self.config.headless,
                tracker=self.tracker,
                user_agent=ua,
                viewport=vp,
                force_144p=self.config.force_low_quality,
                mute_audio=self.config.mute_audio,
            )

    async def run(self) -> None:
        """Executes the full campaign."""
        print("=" * 70)
        print("CORETERON YOUTUBE VIEW AUTOMATION SUITE")
        print("=" * 70)
        print(f"Target URL:         {self.config.target_url}")
        print(f"Target Views:       {self.config.target_views}")
        print(f"Concurrency:        {self.config.concurrency} concurrent browser sessions")
        print(f"Watch Duration:     {self.config.min_watch_seconds}s - {self.config.max_watch_seconds}s per view")
        print(f"Headless Mode:      {'Enabled' if self.config.headless else 'Disabled (Visible Browser)'}")
        print(f"144p Optimization:  {'Enabled (88% Bandwidth Reduction)' if self.config.force_low_quality else 'Disabled'}")
        print(f"Configured Proxies: {self.proxy_mgr.total_proxies} loaded")
        print("=" * 70)
        print("Starting execution...\n")

        start_time = time.time()
        tasks = [self._worker_task(i + 1, self.config.target_views) for i in range(self.config.target_views)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.time() - start_time
        summary = self.tracker.get_summary()

        print("\n" + "=" * 70)
        print("CAMPAIGN EXECUTION COMPLETE")
        print("=" * 70)
        print(f"Total Views Attempted:  {summary['total']}")
        print(f"Successful Views:       {summary['successful']}")
        print(f"Failed / Retrying:      {summary['failed']}")
        print(f"Success Rate:           {summary['rate']}%")
        print(f"Total Wall-Clock Time:  {round(elapsed, 1)} seconds")
        print(f"Detailed CSV Log:       {self.tracker.csv_path}")
        print(f"Summary JSON:           {self.tracker.json_path}")
        print("=" * 70)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Coreteron YouTube View Automation Suite")
    parser.add_argument("--url", type=str, help="Target YouTube Video URL")
    parser.add_argument("--views", type=int, default=5, help="Number of views to achieve (default: 5)")
    parser.add_argument("--concurrency", type=int, default=2, help="Number of concurrent workers (default: 2)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--proxy-file", type=str, help="Path to proxies.txt")
    parser.add_argument("--gateway", type=str, help="Rotating proxy gateway URL (e.g. http://user:pass@host:port)")
    parser.add_argument("--min-watch", type=int, default=35, help="Minimum watch seconds (default: 35)")
    parser.add_argument("--max-watch", type=int, default=65, help="Maximum watch seconds (default: 65)")

    args = parser.parse_args()

    cfg = BotConfig()
    if args.url:
        cfg.target_url = args.url
    if args.views:
        cfg.target_views = args.views
    if args.concurrency:
        cfg.concurrency = args.concurrency
    if args.headless:
        cfg.headless = True
    if args.proxy_file:
        cfg.proxy_file = args.proxy_file
    if args.gateway:
        cfg.rotating_gateway = args.gateway
    if args.min_watch:
        cfg.min_watch_seconds = args.min_watch
    if args.max_watch:
        cfg.max_watch_seconds = args.max_watch

    runner = CampaignRunner(cfg)
    asyncio.run(runner.run())


if __name__ == "__main__":
    main()
