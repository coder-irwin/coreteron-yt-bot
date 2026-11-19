#!/usr/bin/env python3
"""Stealth and Anti-Detection context engine for Playwright.

Neutralizes common bot detection vectors including navigator.webdriver,
WebGL fingerprinting, permissions API, and automation flags.
"""

from __future__ import annotations

import random
from typing import Dict, Tuple
from playwright.async_api import BrowserContext, Page

STEALTH_SCRIPTS = """
(() => {
    // 1. Remove navigator.webdriver flag
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
    });

    // 2. Mock realistic Chrome runtime
    window.chrome = {
        app: {
            isInstalled: false,
            InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
            RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }
        },
        runtime: {
            OnInstalledReason: { CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update' },
            OnRestartRequiredReason: { APP_UPDATE: 'app_update', OS_UPDATE: 'os_update', PERIODIC: 'periodic' },
            PlatformArch: { ARM: 'arm', ARM64: 'arm64', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' },
            PlatformNaclArch: { ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' },
            PlatformOs: { ANDROID: 'android', CROS: 'cros', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win' },
            RequestUpdateCheckStatus: { NO_UPDATE: 'no_update', THROTTLED: 'throttled', UPDATE_AVAILABLE: 'update_available' }
        }
    };

    // 3. Spoof realistic plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            { name: 'PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
            { name: 'Chrome PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
            { name: 'Chromium PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }
        ],
    });

    // 4. Overwrite Permissions query for notifications
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );

    // 5. Spoof realistic WebGL Vendor and Renderer
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        // UNMASKED_VENDOR_WEBGL
        if (parameter === 37445) {
            return 'Google Inc. (NVIDIA)';
        }
        // UNMASKED_RENDERER_WEBGL
        if (parameter === 37446) {
            return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)';
        }
        return getParameter.apply(this, arguments);
    };

    if (window.WebGL2RenderingContext) {
        const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Google Inc. (NVIDIA)';
            }
            if (parameter === 37446) {
                return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)';
            }
            return getParameter2.apply(this, arguments);
        };
    }
})();
"""


async def apply_stealth_to_page(page: Page) -> None:
    """Injects stealth scripts to execute before any page JavaScript runs."""
    await page.add_init_script(STEALTH_SCRIPTS)


def get_randomized_browser_args() -> list[str]:
    """Returns standardized chromium launch arguments that disable telemetry and automation banners."""
    return [
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--no-first-run",
        "--no-service-autorun",
        "--password-store=basic",
        "--lang=en-US,en",
    ]
