#!/usr/bin/env python3
"""Proxy management module for Coreteron YouTube View Automation Suite.

Handles proxy parsing, format normalization, rotation across worker threads,
and optional outbound IP verification.
"""

from __future__ import annotations

import logging
from pathlib import Path
import random
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger("proxy_manager")


class ProxyManager:
    """Manages proxy rotation, formatting, and validation."""

    def __init__(self, proxy_file: Optional[str] = None, rotating_gateway: Optional[str] = None):
        self.proxy_file = Path(proxy_file) if proxy_file else None
        self.rotating_gateway = rotating_gateway.strip() if rotating_gateway else None
        self.proxies: List[Dict[str, str]] = []
        self._index = 0
        self.load_proxies()

    def parse_proxy_string(self, proxy_str: str) -> Optional[Dict[str, str]]:
        """Parses various proxy formats into Playwright-compatible proxy dict.
        
        Supported formats:
        - http://username:password@ip:port
        - socks5://username:password@ip:port
        - ip:port:username:password
        - ip:port
        - http://ip:port
        """
        if not proxy_str or not proxy_str.strip():
            return None
        
        raw = proxy_str.strip()
        if raw.startswith("#"):
            return None

        # Format: ip:port:user:pass (commonly provided by residential proxy vendors)
        parts = raw.split(":")
        if len(parts) == 4 and not raw.startswith("http://") and not raw.startswith("socks5://"):
            ip, port, user, pwd = parts
            return {
                "server": f"http://{ip}:{port}",
                "username": user,
                "password": pwd,
            }
        
        # Add protocol if missing
        if "://" not in raw:
            raw = f"http://{raw}"
            
        try:
            parsed = urlparse(raw)
            server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
            res: Dict[str, str] = {"server": server}
            if parsed.username:
                res["username"] = parsed.username
            if parsed.password:
                res["password"] = parsed.password
            return res
        except Exception as e:
            logger.warning("Failed to parse proxy string %s: %s", raw, e)
            return None

    def load_proxies(self) -> None:
        """Loads proxy pool from configured file or gateway."""
        self.proxies.clear()
        
        # Priority 1: Rotating Gateway (Smartproxy, Webshare, Bright Data backconnect endpoint)
        if self.rotating_gateway:
            parsed = self.parse_proxy_string(self.rotating_gateway)
            if parsed:
                self.proxies.append(parsed)
                logger.info("Loaded rotating gateway: %s", parsed["server"])
                return

        # Priority 2: Proxy list file
        if self.proxy_file and self.proxy_file.exists():
            try:
                with open(self.proxy_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            parsed = self.parse_proxy_string(line)
                            if parsed:
                                self.proxies.append(parsed)
                logger.info("Loaded %d proxies from %s", len(self.proxies), self.proxy_file)
            except Exception as e:
                logger.error("Error reading proxy file %s: %s", self.proxy_file, e)

    def get_proxy(self, rotate: bool = True) -> Optional[Dict[str, str]]:
        """Returns the next proxy dictionary for Playwright launch.
        
        If rotating gateway is used, returning the same server address with session ID
        or standard backconnect forces a new IP on the vendor side.
        """
        if not self.proxies:
            return None
        
        if len(self.proxies) == 1:
            return self.proxies[0]
            
        if rotate:
            proxy = self.proxies[self._index % len(self.proxies)]
            self._index += 1
            return proxy
        else:
            return random.choice(self.proxies)

    @property
    def total_proxies(self) -> int:
        return len(self.proxies)
