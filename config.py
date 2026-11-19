#!/usr/bin/env python3
"""Configuration module for Coreteron YouTube View Automation Suite.

Zero-dependency configuration with environment variable and CLI overrides.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import List, Tuple

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class BotConfig:
    # Target video URL (Coreteron Showcase Video)
    target_url: str = "https://youtu.be/DwRt5d-3AWc?si=8up-r-mjItwVYKMf"
    
    # Concurrency and scale
    target_views: int = 5
    concurrency: int = 2
    
    # Watch duration parameters (in seconds)
    # Target video total length is 141.5s (~2m 21s)
    # 35s - 70s delivers ~25% - 50% retention curve (optimal for organic ML audit retention)
    min_watch_seconds: int = 35
    max_watch_seconds: int = 70
    
    # Bandwidth optimization: force video quality to 'tiny' (144p)
    # Reduces bandwidth consumption per view from ~2.5 MB (720p) to ~0.3 MB (144p)
    # Saves up to 88% on residential proxy bandwidth costs
    force_low_quality: bool = True
    
    # Browser display mode (True = visible browser for demo, False = headless for production)
    headless: bool = False
    
    # Proxy configuration
    # Can be a single rotating gateway (e.g. 'http://user:pass@proxy.provider.com:7000')
    # or a path to a file with proxy list
    proxy_file: str = str(BASE_DIR / "proxies.txt")
    rotating_gateway: str = ""
    
    # Behavior emulation
    emulate_human_mouse: bool = True
    emulate_human_scroll: bool = True
    randomize_viewport: bool = True
    mute_audio: bool = True
    
    # Viewport presets for fingerprint diversification
    viewports: List[Tuple[int, int]] = field(
        default_factory=lambda: [
            (1920, 1080),
            (1440, 900),
            (1366, 768),
            (1536, 864),
            (1280, 800),
            (1600, 900),
        ]
    )

    # Realistic User-Agent pool
    user_agents: List[str] = field(
        default_factory=lambda: [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        ]
    )
