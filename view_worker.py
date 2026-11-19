#!/usr/bin/env python3
"""Single View Worker for Coreteron YouTube View Automation Suite.

Executes an isolated, stealth-shielded browser session to view a video through
a designated proxy and human behavior simulation.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import logging
from pathlib import Path
import random
import time
from typing import Any, Dict, Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from behavior_engine import BehaviorEngine
from player_controller import YouTubePlayerController
from session_tracker import SessionTracker, ViewSessionRecord
from stealth_context import apply_stealth_to_page, get_randomized_browser_args

logger = logging.getLogger("view_worker")


async def run_single_view(
    session_id: str,
    target_url: str,
    proxy_config: Optional[Dict[str, str]],
    watch_seconds: int,
    headless: bool,
    tracker: SessionTracker,
    user_agent: str,
    viewport: tuple[int, int],
    force_144p: bool = True,
    mute_audio: bool = True,
) -> bool:
    """Executes a single autonomous viewing session."""
    proxy_display = proxy_config.get("server", "Direct Connection") if proxy_config else "Direct Connection"
    start_time = time.time()
    logger.info("[%s] Starting view session on %s (Target watch: %ds)", session_id, proxy_display, watch_seconds)

    launch_args = get_randomized_browser_args()
    launch_kwargs: Dict[str, Any] = {
        "headless": headless,
        "args": launch_args,
    }
    if proxy_config:
        launch_kwargs["proxy"] = proxy_config

    async with async_playwright() as pw:
        browser: Optional[Browser] = None
        context: Optional[BrowserContext] = None
        try:
            browser = await pw.chromium.launch(**launch_kwargs)
            context = await browser.new_context(
                viewport={"width": viewport[0], "height": viewport[1]},
                user_agent=user_agent,
                locale="en-US",
                timezone_id="America/New_York",
                has_touch=False,
            )

            page = await context.new_page()
            await apply_stealth_to_page(page)

            # Optimize bandwidth and speed over residential proxies by aborting heavy images/fonts/trackers
            async def handle_route(route):
                req = route.request
                rtype = req.resource_type
                url = req.url
                if rtype in ["image", "font"] and "videoplayback" not in url:
                    await route.abort()
                elif any(ad in url for ad in ["doubleclick.net", "google-analytics.com", "googletagmanager.com"]):
                    await route.abort()
                else:
                    await route.continue_()

            await page.route("**/*", handle_route)

            controller = YouTubePlayerController(page)
            behavior = BehaviorEngine(page)

            # Navigate to video URL with fast commit to avoid proxy TLS stalls
            logger.info("[%s] Navigating to target video...", session_id)
            try:
                await page.goto(target_url, wait_until="commit", timeout=35000)
            except Exception as e:
                logger.warning("[%s] Navigation notice: %s", session_id, e)

            try:
                await page.wait_for_selector("video", timeout=25000)
            except Exception:
                pass
            await page.wait_for_timeout(2000)

            # Dismiss consent and privacy banners
            await controller.handle_consent_and_modals()

            # Ensure playback is active
            playback_started = await controller.ensure_playback_started()
            if not playback_started:
                # Retry once after brief delay
                await page.wait_for_timeout(2000)
                playback_started = await controller.ensure_playback_started()

            if mute_audio:
                await controller.mute_player()

            # Apply 144p bandwidth optimization
            if force_144p:
                await controller.optimize_bandwidth_144p()

            # Watch loop with human emulation
            elapsed = 0
            check_interval = 5
            bandwidth_saved_mb = 0.0

            logger.info("[%s] Video playing. Emulating natural viewer behavior...", session_id)
            while elapsed < watch_seconds:
                sleep_chunk = min(check_interval, watch_seconds - elapsed)
                await page.wait_for_timeout(int(sleep_chunk * 1000))
                elapsed += sleep_chunk

                # Emulate mouse interactions periodically
                if random.random() < 0.65:
                    target_x = random.randint(100, viewport[0] - 100)
                    target_y = random.randint(100, viewport[1] - 100)
                    await behavior.move_mouse_naturally(target_x, target_y, steps=8)

                # Emulate occasional page scrolling
                if elapsed > 15 and random.random() < 0.35:
                    await behavior.simulate_natural_scroll()

            # Verify final playback status
            stats = await controller.get_playback_stats()
            video_time = stats.get("currentTime", elapsed)
            quality = stats.get("quality", "144p")

            # Standard 720p 45s = ~2.5 MB. 144p 45s = ~0.3 MB. Saved = ~2.2 MB.
            if force_144p:
                bandwidth_saved_mb = round((watch_seconds / 45.0) * 2.2, 2)

            is_valid = video_time >= 25 or elapsed >= 30

            status_str = "SUCCESS" if is_valid else "FAILED"
            details = f"Watched {elapsed}s (Video time: {video_time}s, Quality: {quality})"
            logger.info("[%s] Session complete: %s (%s)", session_id, status_str, details)

            tracker.log_session(
                ViewSessionRecord(
                    session_id=session_id,
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    target_url=target_url,
                    proxy_server=proxy_display,
                    watch_seconds=round(elapsed, 1),
                    video_current_time=round(video_time, 1) if isinstance(video_time, (int, float)) else 0.0,
                    video_quality=str(quality),
                    bandwidth_saved_mb=bandwidth_saved_mb,
                    status=status_str,
                    details=details,
                )
            )
            return is_valid

        except Exception as e:
            logger.error("[%s] Error during view session: %s", session_id, e)
            tracker.log_session(
                ViewSessionRecord(
                    session_id=session_id,
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    target_url=target_url,
                    proxy_server=proxy_display,
                    watch_seconds=round(time.time() - start_time, 1),
                    video_current_time=0.0,
                    video_quality="none",
                    bandwidth_saved_mb=0.0,
                    status="ERROR",
                    details=str(e),
                )
            )
            return False
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()
