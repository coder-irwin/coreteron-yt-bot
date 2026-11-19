#!/usr/bin/env python3
"""Flask Web Application for Coreteron YouTube View Automation Suite.

Provides a real-time web dashboard for:
- Configuring and initiating automated viewing campaigns
- Live telemetry streaming via Server-Sent Events (SSE)
- Dynamic 144p bandwidth savings tracker
- Proxy connectivity and latency diagnostics
- Execution audit history and metrics
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import queue
import threading
import time
from typing import Any, Dict, Optional
import urllib.request

from flask import Flask, Response, jsonify, render_template, request, send_file

from config import BotConfig, RESULTS_DIR
from proxy_manager import ProxyManager
from session_tracker import SessionTracker, ViewSessionRecord
from view_worker import run_single_view

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Load .env configuration
env_path = BASE_DIR / ".env"
if env_path.exists():
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception:
        pass

app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
app.config["SECRET_KEY"] = "coreteron_yt_secure_key_2026"

# Global State & SSE Queue
event_queue: queue.Queue = queue.Queue(maxsize=1000)
campaign_thread: Optional[threading.Thread] = None
is_campaign_running = False
stop_requested = threading.Event()
campaign_stats = {
    "status": "idle",
    "target_url": "",
    "target_views": 0,
    "completed_views": 0,
    "successful_views": 0,
    "failed_views": 0,
    "bandwidth_saved_mb": 0.0,
    "start_time": None,
}


def publish_event(event_type: str, title: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
    payload = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "type": event_type,
        "title": title,
        "message": message,
        "data": data or {},
    }
    try:
        event_queue.put_nowait(payload)
    except queue.Full:
        pass


@app.route("/")
def index():
    return render_template(
        "index.html",
        default_target_url=os.getenv("TARGET_URL", "https://youtu.be/DwRt5d-3AWc?si=8up-r-mjItwVYKMf"),
        default_proxy_gateway=os.getenv("PROXY_GATEWAY", "http://olqlayvv-rotate:a1ahaeqjq3df@p.webshare.io:80"),
        default_target_views=os.getenv("TARGET_VIEWS", "5"),
        default_concurrency=os.getenv("CONCURRENCY", "2"),
        default_min_watch=os.getenv("MIN_WATCH_SECONDS", "35"),
        default_max_watch=os.getenv("MAX_WATCH_SECONDS", "65"),
    )


@app.route("/api/status")
def api_status():
    tracker = SessionTracker()
    summary = tracker.get_summary()
    return jsonify({
        "is_running": is_campaign_running,
        "stats": campaign_stats,
        "history_summary": summary,
    })


@app.route("/api/campaign/start", methods=["POST"])
def api_start_campaign():
    global is_campaign_running, campaign_thread, stop_requested, campaign_stats

    if is_campaign_running:
        return jsonify({"success": False, "message": "A campaign is already actively running."}), 400

    data = request.json or {}
    url = str(data.get("url", "")).strip() or "https://youtu.be/DwRt5d-3AWc?si=8up-r-mjItwVYKMf"
    
    try:
        target_views = max(1, int(data.get("target_views", 5)))
        concurrency = max(1, min(20, int(data.get("concurrency", 2))))
        min_watch = max(30, int(data.get("min_watch", 35)))
        max_watch = max(min_watch, int(data.get("max_watch", 65)))
    except ValueError:
        return jsonify({"success": False, "message": "Invalid numeric parameters."}), 400

    gateway = str(data.get("gateway", "")).strip()
    headless = bool(data.get("headless", False))
    force_144p = bool(data.get("force_144p", True))

    stop_requested.clear()
    campaign_stats = {
        "status": "running",
        "target_url": url,
        "target_views": target_views,
        "completed_views": 0,
        "successful_views": 0,
        "failed_views": 0,
        "bandwidth_saved_mb": 0.0,
        "start_time": datetime.now().strftime("%H:%M:%S"),
    }

    def worker_loop():
        global is_campaign_running
        is_campaign_running = True
        publish_event("info", "Campaign Initialized", f"Target: {target_views} views on {url} (Concurrency: {concurrency})")

        cfg = BotConfig(
            target_url=url,
            target_views=target_views,
            concurrency=concurrency,
            min_watch_seconds=min_watch,
            max_watch_seconds=max_watch,
            headless=headless,
            force_low_quality=force_144p,
            rotating_gateway=gateway,
        )

        proxy_mgr = ProxyManager(proxy_file=cfg.proxy_file, rotating_gateway=cfg.rotating_gateway)
        tracker = SessionTracker()

        async def run_all():
            sem = asyncio.Semaphore(concurrency)

            async def run_single(idx: int):
                if stop_requested.is_set():
                    return
                session_id = f"WORKER-{idx:03d}"
                prx = proxy_mgr.get_proxy(rotate=True)
                prx_label = prx.get("server", "Direct") if prx else "Direct Connection"
                watch_time = min_watch if min_watch == max_watch else int(min_watch + (idx % (max_watch - min_watch + 1)))

                async with sem:
                    if stop_requested.is_set():
                        return
                    publish_event("worker_start", "Worker Started", f"[{session_id}] Connecting via {prx_label} (Watch: {watch_time}s)")
                    success = await run_single_view(
                        session_id=session_id,
                        target_url=url,
                        proxy_config=prx,
                        watch_seconds=watch_time,
                        headless=headless,
                        tracker=tracker,
                        user_agent=cfg.user_agents[idx % len(cfg.user_agents)],
                        viewport=cfg.viewports[idx % len(cfg.viewports)],
                        force_144p=force_144p,
                        mute_audio=True,
                    )
                    campaign_stats["completed_views"] += 1
                    if success:
                        campaign_stats["successful_views"] += 1
                        campaign_stats["bandwidth_saved_mb"] += round((watch_time / 45.0) * 2.2, 2)
                        publish_event("worker_success", "View Verified", f"[{session_id}] Verified >= 30s playback on {prx_label}")
                    else:
                        campaign_stats["failed_views"] += 1
                        publish_event("worker_fail", "View Failed", f"[{session_id}] Session incomplete or interrupted")

            tasks = [run_single(i + 1) for i in range(target_views)]
            await asyncio.gather(*tasks, return_exceptions=True)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_all())
        finally:
            loop.close()

        is_campaign_running = False
        campaign_stats["status"] = "completed" if not stop_requested.is_set() else "stopped"
        publish_event("complete", "Campaign Finished", f"Finished {campaign_stats['completed_views']}/{target_views} views. Success: {campaign_stats['successful_views']}")

    campaign_thread = threading.Thread(target=worker_loop, daemon=True)
    campaign_thread.start()

    return jsonify({"success": True, "message": "Campaign launched successfully."})


@app.route("/api/campaign/stop", methods=["POST"])
def api_stop_campaign():
    global stop_requested, is_campaign_running
    if not is_campaign_running:
        return jsonify({"success": False, "message": "No campaign is currently running."})

    stop_requested.set()
    publish_event("warning", "Stop Requested", "Stopping all workers cleanly after current sessions...")
    return jsonify({"success": True, "message": "Stop signal delivered."})


@app.route("/api/proxy/test", methods=["POST"])
def api_test_proxy():
    import base64
    import urllib.error

    data = request.json or {}
    proxy_str = str(data.get("proxy", "")).strip()
    if not proxy_str:
        return jsonify({"success": False, "message": "Proxy URL is required."}), 400

    mgr = ProxyManager()
    cfg = mgr.parse_proxy_string(proxy_str)
    if not cfg:
        return jsonify({"success": False, "message": "Invalid proxy format. Expected http://user:pass@host:port or host:port:user:pass"}), 400

    server = cfg.get("server", "")
    username = cfg.get("username")
    password = cfg.get("password")

    proxy_url = server
    if username and password:
        parts = server.split("://")
        scheme = parts[0]
        host = parts[1]
        proxy_url = f"{scheme}://{username}:{password}@{host}"

    proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
    handlers = [proxy_handler]

    if username and password:
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, server, username, password)
        auth_handler = urllib.request.ProxyBasicAuthHandler(password_mgr)
        handlers.append(auth_handler)

    opener = urllib.request.build_opener(*handlers)
    # Use HTTP endpoint to test outward IP and avoid HTTPS CONNECT handshake issues
    req = urllib.request.Request("http://api.ipify.org?format=json", headers={"User-Agent": "CoreteronProxyTester/1.0"})
    if username and password:
        auth_bytes = f"{username}:{password}".encode("utf-8")
        req.add_header("Proxy-Authorization", "Basic " + base64.b64encode(auth_bytes).decode("utf-8"))

    start_t = time.time()
    try:
        with opener.open(req, timeout=10) as resp:
            data_resp = json.loads(resp.read().decode())
            latency_ms = round((time.time() - start_t) * 1000)
            return jsonify({
                "success": True,
                "ip": data_resp.get("ip"),
                "latency_ms": latency_ms,
                "message": f"Proxy active. External IP: {data_resp.get('ip')} ({latency_ms}ms)",
            })
    except urllib.error.HTTPError as e:
        if e.code == 407:
            return jsonify({
                "success": False,
                "message": "Proxy Authentication Required (HTTP 407). The proxy server rejected your credentials. Please verify your username and password, or check if your IP must be whitelisted in your proxy provider dashboard.",
            }), 400
        return jsonify({"success": False, "message": f"Proxy HTTP Error {e.code}: {e.reason}"}), 400
    except Exception as e:
        err_msg = str(e)
        if "407" in err_msg:
            return jsonify({
                "success": False,
                "message": "Proxy Authentication Required (HTTP 407). The proxy server rejected your credentials. Please verify your username and password, or check if your IP must be whitelisted in your proxy provider dashboard.",
            }), 400
        return jsonify({"success": False, "message": f"Proxy connection check failed: {err_msg}"}), 500


@app.route("/api/stream")
def api_stream():
    def event_generator():
        while True:
            try:
                event = event_queue.get(timeout=20)
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                yield ": keepalive\n\n"

    return Response(event_generator(), mimetype="text/event-stream")


def start_server(host: str = "127.0.0.1", port: int = 5055, debug: bool = False):
    port = int(os.getenv("PORT", port))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
    )
    print("=" * 65)
    print("  CORETERON YOUTUBE VIEW AUTOMATION DASHBOARD")
    print(f"  Running locally at: http://{host}:{port}")
    print("  144p Dynamic Bandwidth Optimization: ENABLED")
    print("  Anti-Fingerprinting Stealth Shield: ENABLED")
    print("=" * 65)
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    start_server()
