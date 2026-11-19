#!/usr/bin/env python3
"""YouTube Player Controller and Bandwidth Optimization Engine.

Handles:
- Cookie consent and dialog dismissal across international residential IP geolocations
- HTML5 player initialization and playback state verification
- Dynamic quality reduction to 'tiny' (144p) to reduce residential proxy bandwidth by ~88%
- Playback telemetry and heartbeat verification
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger("player_controller")


class YouTubePlayerController:
    """Controls the YouTube HTML5 player via DOM and internal Player APIs."""

    def __init__(self, page: Page):
        self.page = page

    async def handle_consent_and_modals(self) -> bool:
        """Dismisses Google/YouTube cookie consent modals common in European and international residential IPs."""
        consent_selectors = [
            # European / International consent dialog buttons
            "button[aria-label*='Accept all']",
            "button[aria-label*='Accept the use of cookies']",
            "button:has-text('Accept all')",
            "button:has-text('I agree')",
            "button:has-text('Agree')",
            "form[action*='consent'] button",
            "yt-button-renderer:has-text('Accept all') button",
            # YouTube sign-in promo dismissals
            "ytd-button-renderer:has-text('No thanks') button",
            "yt-button-renderer:has-text('Dismiss') button",
            "button[aria-label='Dismiss']",
            "tp-yt-paper-button:has-text('Dismiss')",
        ]

        for selector in consent_selectors:
            try:
                elem = self.page.locator(selector).first
                if await elem.is_visible(timeout=1500):
                    await elem.click(timeout=2000)
                    logger.info("Dismissed modal via selector: %s", selector)
                    await self.page.wait_for_timeout(800)
                    return True
            except Exception:
                continue
        return False

    async def ensure_playback_started(self) -> bool:
        """Ensures the video is actively playing and not paused."""
        try:
            # First attempt: Check HTML5 video element directly
            is_playing = await self.page.evaluate("""() => {
                const v = document.querySelector('video');
                if (!v) return false;
                if (v.paused) {
                    v.play().catch(() => {});
                }
                return !v.paused;
            }""")
            
            if is_playing:
                return True

            # If still not playing, try clicking the big play button or player overlay
            play_btn = self.page.locator(".ytp-play-button, button.ytp-large-play-button").first
            if await play_btn.is_visible(timeout=2000):
                await play_btn.click(timeout=2000)
                await self.page.wait_for_timeout(1000)

            # Check again
            return await self.page.evaluate("""() => {
                const v = document.querySelector('video');
                return v ? !v.paused : false;
            }""")
        except Exception as e:
            logger.debug("Playback start check: %s", e)
            return False

    async def optimize_bandwidth_144p(self) -> bool:
        """Forces video playback quality to 144p (tiny) via internal player API.
        
        Saves ~88% of residential proxy bandwidth by streaming audio + lowest DASH chunk size.
        """
        try:
            success = await self.page.evaluate("""() => {
                const player = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
                if (player) {
                    // Try internal YouTube player API methods
                    if (typeof player.setPlaybackQualityRange === 'function') {
                        player.setPlaybackQualityRange('tiny', 'tiny');
                    }
                    if (typeof player.setPlaybackQuality === 'function') {
                        player.setPlaybackQuality('tiny');
                    }
                    return true;
                }
                return false;
            }""")
            if success:
                logger.info("Optimized video stream to 144p (tiny) to conserve proxy bandwidth.")
                return True
        except Exception as e:
            logger.debug("144p optimization evaluation: %s", e)
        return False

    async def mute_player(self) -> None:
        """Mutes video audio to avoid unwanted sound output during automation."""
        try:
            await self.page.evaluate("""() => {
                const v = document.querySelector('video');
                if (v) v.muted = true;
                const player = document.getElementById('movie_player');
                if (player && typeof player.mute === 'function') {
                    player.mute();
                }
            }""")
        except Exception:
            pass

    async def get_playback_stats(self) -> Dict[str, Any]:
        """Reads real-time HTML5 video telemetry from the DOM."""
        try:
            return await self.page.evaluate("""() => {
                const v = document.querySelector('video');
                const player = document.getElementById('movie_player');
                if (!v) {
                    return { found: false };
                }
                return {
                    found: true,
                    currentTime: Math.round(v.currentTime * 10) / 10,
                    duration: Math.round(v.duration * 10) / 10,
                    paused: v.paused,
                    ended: v.ended,
                    muted: v.muted,
                    quality: (player && typeof player.getPlaybackQuality === 'function') ? player.getPlaybackQuality() : 'unknown',
                    buffered: v.buffered.length > 0 ? Math.round(v.buffered.end(v.buffered.length - 1) * 10) / 10 : 0
                };
            }""")
        except Exception as e:
            return {"found": False, "error": str(e)}
