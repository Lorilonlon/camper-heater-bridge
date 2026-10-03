import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

from bridge.diagnostics import Diagnostics


class DiagnosticsTests(unittest.TestCase):
    def test_changes_heartbeat_errors_and_private_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            diag = Diagnostics(directory)
            backend = SimpleNamespace(advertising=True, registered=True,
                                      restart_required=False, pair_until=0)
            bridge = SimpleNamespace(status="ready", ready=True, mqtt=None, backend=backend,
                                     paused_until=0, updated="2026-01-01T00:00:00Z",
                                     options={"mqtt_password": "DO-NOT-LOG"})
            diag.observe(bridge)
            diag.observe(bridge)
            diag.link({"Connected": True, "Address": "DO-NOT-LOG", "Key": "DO-NOT-LOG"})
            diag.link({"Connected": True})
            bridge.ready = False
            diag.observe(bridge)
            diag.error(TimeoutError("DO-NOT-LOG"))
            with patch("bridge.diagnostics.time.monotonic", return_value=diag.last_heartbeat + 301):
                diag.observe(bridge)
            with zipfile.ZipFile(io.BytesIO(diag.archive())) as archive:
                text = archive.read("connection.log").decode()
            rows = [json.loads(line) for line in text.splitlines()]
            self.assertNotIn("DO-NOT-LOG", text)
            self.assertEqual([r["event"] for r in rows],
                             ["started", "state_changed", "bluetooth_state", "state_changed", "error", "heartbeat"])
            self.assertEqual(rows[-2]["error_type"], "TimeoutError")
            self.assertEqual(Path(directory).stat().st_mode & 0o777, 0o700)
            diag.close()

    def test_rotation_and_restart_keep_bounded_history(self):
        with tempfile.TemporaryDirectory() as directory:
            diag = Diagnostics(directory)
            diag.handler.maxBytes = 2048
            for i in range(100):
                diag.record("sample", value="x" * 400, number=i)
            diag.close()
            files = list(Path(directory).glob("connection.log*"))
            self.assertEqual(len(files), 3)
            self.assertLess(sum(p.stat().st_size for p in files), 3 * 2048)
            diag = Diagnostics(directory)
            with zipfile.ZipFile(io.BytesIO(diag.archive())) as archive:
                self.assertEqual(set(archive.namelist()), {"connection.log", "connection.log.1", "connection.log.2"})
                self.assertIn('"number": 99', archive.read("connection.log").decode())
            diag.close()
