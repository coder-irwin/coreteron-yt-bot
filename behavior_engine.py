#!/usr/bin/env python3
"""Human Behavioral Emulation Engine for YouTube Automation.

Simulates human-like viewer interaction patterns:
- Non-linear curved mouse movements with organic micro-jitters
- Natural viewport scrolling to comments and recommendations
- Organic watch session duration with statistical distribution
- Random micro-interactions (player hover, scroll pauses)
"""

from __future__ import annotations

import asyncio
import math
import random
from typing import Tuple
from playwright.async_api import Page


class BehaviorEngine:
    """Emulates human viewer telemetry to satisfy YouTube engagement heuristics."""

    def __init__(self, page: Page):
        self.page = page

    async def move_mouse_naturally(self, target_x: int, target_y: int, steps: int = 15) -> None:
        """Moves mouse pointer along a simulated curved trajectory with micro-jitters."""
        try:
            # Get current mouse position or default to center
            current_x = random.randint(200, 500)
            current_y = random.randint(200, 400)
            
            # Bezier control point
            control_x = (current_x + target_x) / 2 + random.randint(-80, 80)
            control_y = (current_y + target_y) / 2 + random.randint(-80, 80)

            for i in range(1, steps + 1):
                t = i / steps
                # Quadratic Bezier formula
                x = (1 - t) ** 2 * current_x + 2 * (1 - t) * t * control_x + t ** 2 * target_x
                y = (1 - t) ** 2 * current_y + 2 * (1 - t) * t * control_y + t ** 2 * target_y
                # Add human jitter
                x += random.uniform(-2, 2)
                y += random.uniform(-2, 2)
                
                await self.page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.015, 0.04))
        except Exception:
            pass

    async def simulate_natural_scroll(self) -> None:
        """Simulates browsing behavior by scrolling down to comments/recommendations and back."""
        try:
            # Scroll down in organic increments
            scroll_amount = random.randint(300, 700)
            steps = random.randint(3, 6)
            per_step = scroll_amount // steps
            
            for _ in range(steps):
                await self.page.mouse.wheel(0, per_step + random.randint(-15, 25))
                await asyncio.sleep(random.uniform(0.3, 0.7))
                
            # Pause as if reading comments
            await asyncio.sleep(random.uniform(1.5, 3.5))
            
            # Scroll back up to the video player
            for _ in range(steps):
                await self.page.mouse.wheel(0, -(per_step + random.randint(-10, 20)))
                await asyncio.sleep(random.uniform(0.2, 0.5))
        except Exception:
            pass

    async def perform_player_hover(self) -> None:
        """Hover over the video player to trigger video control bar visibility."""
        try:
            viewport = self.page.viewport_size
            if viewport:
                target_x = viewport["width"] // 2 + random.randint(-100, 100)
                target_y = viewport["height"] // 3 + random.randint(-50, 50)
                await self.move_mouse_naturally(target_x, target_y, steps=10)
                await asyncio.sleep(random.uniform(0.5, 1.2))
        except Exception:
            pass
