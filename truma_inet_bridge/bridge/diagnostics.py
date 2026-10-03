"""Bounded local connection history; no packets, keys or user settings."""
import datetime
import io
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time
import zipfile


class Diagnostics:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.directory.chmod(0o700)
        self.handler = RotatingFileHandler(self.directory / "connection.log",
                                          maxBytes=512 * 1024, backupCount=2, encoding="utf-8")
        self.handler.setFormatter(logging.Formatter("%(message)s"))
        (self.directory / "connection.log").chmod(0o600)
        self.logger = logging.Logger("truma.connection.history", logging.INFO)
        self.logger.addHandler(self.handler)
        self.previous = None
        self.previous_link = None
        self.last_heartbeat = time.monotonic()
        self.last_tick = self.last_heartbeat
        self.record("started", health=self.health())

    @staticmethod
    def health():
        result = {}
        for name in ("io", "memory", "cpu"):
            try:
                result[name + "_pressure"] = Path("/proc/pressure", name).read_text()[:400]
            except OSError:
                pass
        try:
            result["load"] = Path("/proc/loadavg").read_text().split()[:3]
        except OSError:
            pass
        return result

    def record(self, event, **fields):
        self.logger.info(json.dumps({"time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                     "event": event, **fields}, ensure_ascii=False))

    def observe(self, bridge):
        now = time.monotonic()
        state = {"status": bridge.status, "ready": bridge.ready,
                 "mqtt": bool(bridge.mqtt and bridge.mqtt.connected),
                 "advertising": bridge.backend.advertising,
                 "registered": bridge.backend.registered,
                 "restart_required": bridge.backend.restart_required,
                 "pairing": bridge.backend.pair_until > now,
                 "handover": bridge.paused_until > now}
        gap = now - self.last_tick
        self.last_tick = now
        if state != self.previous or now - self.last_heartbeat >= 300 or gap > 30:
            event = "state_changed" if state != self.previous else "heartbeat"
            self.record(event, **state, last_confirmed=bridge.updated,
                        loop_gap_seconds=round(gap, 1), health=self.health())
            self.previous = state
            self.last_heartbeat = now

    def link(self, properties):
        state = {key: properties.get(key) for key in
                 ("Connected", "ServicesResolved", "Paired", "Bonded", "Trusted", "Blocked")}
        if state != self.previous_link:
            self.record("bluetooth_state", **state)
            self.previous_link = state

    def error(self, exc):
        # Keep type and D-Bus error code, not arbitrary payloads or credentials.
        self.record("error", error_type=type(exc).__name__,
                    dbus_error=getattr(exc, "type", None), health=self.health())

    def archive(self):
        self.handler.flush()
        result = io.BytesIO()
        with zipfile.ZipFile(result, "w", zipfile.ZIP_DEFLATED) as archive:
            for name in ("connection.log", "connection.log.1", "connection.log.2"):
                path = self.directory / name
                if path.is_file():
                    archive.writestr(name, path.read_bytes())
        return result.getvalue()

    def close(self):
        self.record("stopped")
        self.handler.close()
