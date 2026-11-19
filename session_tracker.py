#!/usr/bin/env python3
"""Session tracking and reporting engine for Coreteron YouTube View Automation Suite.

Aggregates view attempts, proxy performance, watch duration metrics, and bandwidth savings.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ViewSessionRecord:
    session_id: str
    timestamp: str
    target_url: str
    proxy_server: str
    watch_seconds: float
    video_current_time: float
    video_quality: str
    bandwidth_saved_mb: float
    status: str
    details: str


class SessionTracker:
    """Thread-safe tracker for recording and exporting session metrics."""

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or RESULTS_DIR
        self.records: List[ViewSessionRecord] = []
        self._lock = threading.Lock()
        self.csv_path = self.log_dir / "view_sessions_log.csv"
        self.json_path = self.log_dir / "session_summary.json"
        self._init_csv()

    def _init_csv(self) -> None:
        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "session_id",
                    "timestamp",
                    "target_url",
                    "proxy_server",
                    "watch_seconds",
                    "video_current_time",
                    "video_quality",
                    "bandwidth_saved_mb",
                    "status",
                    "details",
                ])

    def log_session(self, record: ViewSessionRecord) -> None:
        with self._lock:
            self.records.append(record)
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    record.session_id,
                    record.timestamp,
                    record.target_url,
                    record.proxy_server,
                    record.watch_seconds,
                    record.video_current_time,
                    record.video_quality,
                    record.bandwidth_saved_mb,
                    record.status,
                    record.details,
                ])
            self._save_summary()

    def _save_summary(self) -> None:
        total = len(self.records)
        successful = sum(1 for r in self.records if r.status == "SUCCESS")
        total_watch = sum(r.watch_seconds for r in self.records)
        total_bandwidth_saved = sum(r.bandwidth_saved_mb for r in self.records)
        avg_watch = (total_watch / total) if total > 0 else 0.0

        summary = {
            "total_attempts": total,
            "successful_views": successful,
            "failed_attempts": total - successful,
            "success_rate_percent": round((successful / total * 100), 2) if total > 0 else 0.0,
            "average_watch_seconds": round(avg_watch, 1),
            "total_watch_seconds": round(total_watch, 1),
            "estimated_bandwidth_saved_mb": round(total_bandwidth_saved, 2),
            "last_updated": datetime.now().isoformat(),
        }

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            total = len(self.records)
            successful = sum(1 for r in self.records if r.status == "SUCCESS")
            return {
                "total": total,
                "successful": successful,
                "failed": total - successful,
                "rate": round((successful / total * 100), 1) if total > 0 else 0.0,
            }
