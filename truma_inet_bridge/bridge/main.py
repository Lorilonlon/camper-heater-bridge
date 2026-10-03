import asyncio
import contextlib
import datetime
import json
import logging
import os
from pathlib import Path
import signal
import time
from aiohttp import web
from .bluez import BlueZ
from .mqtt import MQTT
from .protocol import (encode_temperature, decode_temperature, decode_choice, FANS, WATER,
                       command_writes, validate_write_reply)

LOG = logging.getLogger(__name__)

class Bridge:
    def __init__(self, options, data=Path("/data"), backend=None):
        self.options, self.data = options, data
        self.backend = backend or BlueZ(options)
        self.ready = False
        self.state = {"mode": "off", "target": None, "fan": "Unbekannt", "water": "Unbekannt"}
        self.updated = None
        self.status = "Bluetooth wird vorbereitet"
        self.error = None
        self.generation = 0
        self.paused_until = 0
        self.last_read = 0
        self.lock = asyncio.Lock()
        self.mqtt = None
        self.inventory = []
        self.command_tasks = set()
        self.stopping = False
        self.last_target = None
        self.diagnostics = None
        try:
            saved = json.loads((data / "last-target.json").read_text())
            from .protocol import encode_temperature
            encode_temperature(saved["target"])
            self.last_target = saved["target"]
        except (FileNotFoundError, ValueError, TypeError, KeyError):
            pass

    def notify(self, status=None):
        if status:
            self.status = status
        if self.mqtt:
            self.mqtt.update()

    def unavailable(self, status):
        if self.ready:
            self.generation += 1
        self.ready = False
        self.notify(status)

    def remember_target(self, target):
        temporary = self.data / "last-target.tmp"
        temporary.write_text(json.dumps({"target": target}))
        temporary.replace(self.data / "last-target.json")
        self.last_target = target

    async def snapshot(self, include_measurements=True):
        # Publish one coherent snapshot; never leave stale controls available
        # when a partial read fails.
        values = {k: await self.backend.read(k) for k in ("temperature", "fan", "water")}
        target = decode_temperature(values["temperature"])
        if target is not None and target != self.last_target:
            self.remember_target(target)
        previous = self.state
        measurements = {k: previous.get(k) for k in ("current_temperature", "voltage", "water_temperature")}
        if include_measurements:
            read_measurements = getattr(self.backend, "measurements", None)
            measurements = await read_measurements() if read_measurements else dict.fromkeys(measurements)
        self.state = {"mode": "heat" if target is not None else "off",
                      "target": target if target is not None else self.last_target,
                      "fan": decode_choice(values["fan"], FANS),
                      "water": decode_choice(values["water"], WATER), **measurements}
        if not self.ready or previous != self.state:
            LOG.info("Confirmed box state: %s", json.dumps(self.state, ensure_ascii=False))
        self.updated = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if include_measurements:
            self.last_read = time.monotonic()
        self.ready = True
        self.error = None
        self.notify("Verbunden – Steuerung bereit" if self.options["allow_control"] else "Verbunden – Lesemodus")

    async def run(self):
        had_link = False
        while not self.stopping:
            try:
                if self.diagnostics:
                    self.diagnostics.observe(self)
                if not self.backend.registered or self.backend.restart_required:
                    self.unavailable("Bluetooth-Dienst wird verbunden")
                    had_link = False
                    self.generation += 1
                    await self.backend.restart()
                if time.monotonic() < self.paused_until:
                    self.unavailable("Für Truma-App freigegeben")
                    await asyncio.sleep(1)
                    continue
                if not self.backend.advertising:
                    await self.backend.advertise(True)
                props = await self.backend.device()
                if self.diagnostics:
                    self.diagnostics.link(props)
                if not props.get("Connected") or not props.get("ServicesResolved") or not props.get("Paired"):
                    if had_link:
                        self.backend.paths = {}
                        self.backend.subscriptions = []
                        self.generation += 1
                        had_link = False
                    self.unavailable("Kopplung aktiv – Bluetooth-Taste an der Box drücken" if
                                     self.backend.pair_until > time.monotonic() else "Warte auf iNet-Box")
                    await asyncio.sleep(1)
                    continue
                if not had_link:
                    async with self.lock:
                        self.inventory = await self.backend.discover()
                        (self.data / "gatt-inventory.json").write_text(json.dumps(self.inventory, indent=2))
                        self.generation += 1
                        await self.snapshot()
                        await self.backend.trust_verified_box()
                        had_link = True
                    await self.backend.close_pairing()
                elif time.monotonic() - self.last_read >= self.options.get("poll_seconds", 15):
                    async with self.lock:
                        await self.snapshot()
                # Signals from ReadValue itself must not create a busy poll loop.
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.error = str(exc) or type(exc).__name__
                self.unavailable("Verbindung prüfen: " + self.error[:170])
                if self.diagnostics:
                    self.diagnostics.error(exc)
                LOG.warning("Bluetooth read/connect failed (%s): %s", type(exc).__name__, exc)
                had_link = False
                await asyncio.sleep(5)

    def schedule_command(self, kind, value, generation):
        if len(self.command_tasks) >= 4:
            self.notify("Befehl abgewiesen – zu viele gleichzeitige Aufträge")
            return
        task = asyncio.create_task(self.command(kind, value, generation, time.monotonic()))
        self.command_tasks.add(task)
        task.add_done_callback(self.command_tasks.discard)

    async def command(self, kind, value, generation, arrived=None):
        arrived = time.monotonic() if arrived is None else arrived
        try:
            async with self.lock:
                if not self.options["allow_control"]:
                    raise ValueError("Steuerung ist gesperrt: Lesemodus")
                if (self.stopping or time.monotonic() < self.paused_until or
                        not self.ready or getattr(self.backend, "restart_required", False) or
                        generation != self.generation or time.monotonic() - arrived > 3):
                    raise ValueError("Keine aktuelle Verbindung; Befehl verworfen")
                props = await self.backend.device()
                if not props.get("Connected") or not props.get("Paired") or not props.get("ServicesResolved"):
                    raise ValueError("Bluetooth-Verbindung nicht bereit")
                # Re-read the physical state before composing a multi-step command.
                await self.snapshot(include_measurements=False)
                # Reads may take several seconds. Revalidate immediately before
                # changing anything, including a local preset.
                if (self.stopping or time.monotonic() < self.paused_until or
                        getattr(self.backend, "restart_required", False) or
                        generation != self.generation or time.monotonic() - arrived > 3):
                    raise ValueError("Befehl während der Prüfung veraltet; verworfen")
                if kind == "temperature" and self.state["mode"] == "off":
                    # A nonzero box temperature also enables heating. While off,
                    # keep the user's preset locally until an explicit heat command.
                    target = decode_temperature(encode_temperature(value))
                    self.remember_target(target)
                    self.state["target"] = target
                    self.notify()
                    return
                writes = command_writes(kind, value, self.state)
                self.notify("Änderung wird bestätigt")
                for field, payload in writes:
                    if (generation != self.generation or self.stopping or
                            getattr(self.backend, "restart_required", False)):
                        raise ValueError("Verbindung geändert; Befehl abgebrochen")
                    await self.backend.write(field, payload)
                    actual = await self.backend.read(field)
                    if not validate_write_reply(payload, actual):
                        raise ValueError("Die Box hat die Änderung nicht bestätigt")
                await self.snapshot(include_measurements=False)
        except Exception as exc:
            self.error = str(exc)
            # A write may have partially succeeded. Invalidate the entire state
            # until the polling loop has read it again. No retries/replay.
            self.unavailable("Befehl nicht abgeschlossen: " + str(exc)[:160])
            LOG.warning("Command rejected/failed: %s", exc)

    async def handover(self):
        async with self.lock:
            self.generation += 1
            self.paused_until = time.monotonic() + 300
            await self.backend.close_pairing()
            await self.backend.advertise(False)
            await self.backend.disconnect()
            self.unavailable("Für Truma-App freigegeben")

    async def resume(self):
        self.paused_until = 0
        await self.backend.advertise(True)

    def public_status(self):
        return {"status": self.status, "error": self.error, "ready": self.ready,
                "state": self.state if self.ready else None, "updated": self.updated,
                "read_only": not self.options["allow_control"], "mqtt": bool(self.mqtt and self.mqtt.connected),
                "pair_seconds": max(0, int(self.backend.pair_until - time.monotonic())),
                "pause_seconds": max(0, int(self.paused_until - time.monotonic())),
                "advertising": self.backend.advertising, "box": self.options["box_address"],
                "characteristics": len(self.inventory)}

@web.middleware
async def ingress_only(request, handler):
    # The port is not exposed to the LAN. HA ingress is the only trusted caller.
    if request.remote != "172.30.32.2":
        raise web.HTTPForbidden(text="Bitte über Home Assistant öffnen.")
    if request.method == "POST" and request.headers.get("X-Truma-Action") != "1":
        raise web.HTTPForbidden(text="Ungültige Anfrage")
    return await handler(request)

def create_web(bridge):
    app = web.Application(middlewares=[ingress_only])

    async def index(request):
        return web.FileResponse(Path(__file__).with_name("index.html"))

    async def status(request):
        return web.json_response(bridge.public_status())

    async def diagnostics(request):
        if not bridge.diagnostics:
            raise web.HTTPNotFound()
        return web.Response(body=bridge.diagnostics.archive(), content_type="application/zip",
                            headers={"Content-Disposition": 'attachment; filename="truma-connection-history.zip"',
                                     "Cache-Control": "no-store"})

    async def action(request):
        action_name = request.match_info["action"]
        try:
            if action_name == "pair":
                await bridge.resume()
                await bridge.backend.pair()
            elif action_name == "cancel":
                await bridge.backend.close_pairing()
            elif action_name == "handover":
                await bridge.handover()
            elif action_name == "resume":
                await bridge.resume()
            else:
                raise ValueError("Unbekannte Aktion")
            return web.json_response(bridge.public_status())
        except Exception as exc:
            LOG.warning("UI action failed: %s", exc)
            return web.json_response({"error": str(exc)}, status=400)

    app.router.add_get("/", index)
    app.router.add_get("/api/status", status)
    app.router.add_get("/api/diagnostics", diagnostics)
    app.router.add_post("/api/{action}", action)
    return app

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    options = json.loads(Path("/data/options.json").read_text())
    bridge = Bridge(options)
    from .diagnostics import Diagnostics
    bridge.diagnostics = Diagnostics(bridge.data / "diagnostics")
    bridge.mqtt = MQTT(bridge, options)
    bridge.mqtt.start()
    runner = web.AppRunner(create_web(bridge), access_log=None)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 8099).start()
    stop = asyncio.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        asyncio.get_running_loop().add_signal_handler(sig, stop.set)
    task = asyncio.create_task(bridge.run())
    task.add_done_callback(lambda t: stop.set() if not t.cancelled() else None)
    await stop.wait()
    bridge.stopping = True
    for pending in bridge.command_tasks:
        pending.cancel()
    if bridge.command_tasks:
        await asyncio.gather(*bridge.command_tasks, return_exceptions=True)
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        try:
            await task
        except Exception:
            LOG.exception("Bridge stopped unexpectedly")
    bridge.unavailable("Bridge beendet")
    await bridge.backend.stop()
    await asyncio.to_thread(bridge.mqtt.stop)
    await runner.cleanup()
    bridge.diagnostics.close()

if __name__ == "__main__":
    asyncio.run(main())
