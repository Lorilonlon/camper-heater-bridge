import asyncio
import logging
import re
import time
from dbus_next import Message, MessageType, Variant, BusType, DBusError
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method, dbus_property
from dbus_next.constants import PropertyAccess
from .protocol import ADVERTISED_UUID, PHONE_SERVICE, PHONE_CHARACTERISTIC, HEATER_SERVICE, CHARACTERISTICS, MEASUREMENT_SERVICE, MEASUREMENTS, decode_measurement

LOG = logging.getLogger(__name__)
ROOT = "/com/truma/bridge"
SERVICE = ROOT + "/service0"
CHAR = SERVICE + "/char0"
AGENT = ROOT + "/agent"
ADV = ROOT + "/advertisement"
PROPS = "org.freedesktop.DBus.Properties"
DEVICE = "org.bluez.Device1"
GATT = "org.bluez.GattCharacteristic1"
OM = "org.freedesktop.DBus.ObjectManager"

def plain(v):
    if isinstance(v, Variant):
        return plain(v.value)
    if isinstance(v, dict):
        return {k: plain(x) for k, x in v.items()}
    if isinstance(v, list):
        return [plain(x) for x in v]
    return v

class Advertisement(ServiceInterface):
    def __init__(self):
        super().__init__("org.bluez.LEAdvertisement1")

    @dbus_property(access=PropertyAccess.READ)
    def Type(self) -> 's':
        return "peripheral"

    @dbus_property(access=PropertyAccess.READ)
    def ServiceUUIDs(self) -> 'as':
        return [ADVERTISED_UUID]

    @dbus_property(access=PropertyAccess.READ)
    def LocalName(self) -> 's':
        return "Truma HA"

    @dbus_property(access=PropertyAccess.READ)
    def Discoverable(self) -> 'b':
        return True

    @method()
    def Release(self):
        LOG.info("Bluetooth advertisement released")

class PhoneService(ServiceInterface):
    def __init__(self):
        super().__init__("org.bluez.GattService1")

    @dbus_property(access=PropertyAccess.READ)
    def UUID(self) -> 's':
        return PHONE_SERVICE

    @dbus_property(access=PropertyAccess.READ)
    def Primary(self) -> 'b':
        return True

class PhoneCharacteristic(ServiceInterface):
    def __init__(self, backend):
        super().__init__(GATT)
        self.backend = backend
        self.notifying = False

    @dbus_property(access=PropertyAccess.READ)
    def UUID(self) -> 's':
        return PHONE_CHARACTERISTIC

    @dbus_property(access=PropertyAccess.READ)
    def Service(self) -> 'o':
        return SERVICE

    @dbus_property(access=PropertyAccess.READ)
    def Flags(self) -> 'as':
        return ["read", "notify"]

    @dbus_property(access=PropertyAccess.READ)
    def Notifying(self) -> 'b':
        return self.notifying

    @method()
    def ReadValue(self, options: 'a{sv}') -> 'ay':
        device = plain(options).get("device")
        if device != self.backend.device_path:
            raise DBusError("org.bluez.Error.NotAuthorized", "Unbekannte Gegenstelle")
        # The capture has subscription only, no read or notification payload.
        # Do not invent a response to an as-yet unknown protocol operation.
        LOG.warning("Box requested the phone characteristic; payload semantics not yet known")
        raise DBusError("org.bluez.Error.NotSupported", "Payload noch nicht entschlüsselt")

    @method()
    def StartNotify(self):
        self.notifying = True
        self.emit_properties_changed({"Notifying": True})
        LOG.info("Box subscribed to phone service")

    @method()
    def StopNotify(self):
        self.notifying = False
        self.emit_properties_changed({"Notifying": False})

class Application(ServiceInterface):
    def __init__(self):
        super().__init__(OM)

    @method()
    def GetManagedObjects(self) -> 'a{oa{sa{sv}}}':
        return {
            SERVICE: {"org.bluez.GattService1": {
                "UUID": Variant("s", PHONE_SERVICE), "Primary": Variant("b", True)}},
            CHAR: {GATT: {
                "UUID": Variant("s", PHONE_CHARACTERISTIC),
                "Service": Variant("o", SERVICE), "Flags": Variant("as", ["read", "notify"])}},
        }

class Agent(ServiceInterface):
    def __init__(self, backend):
        super().__init__("org.bluez.Agent1")
        self.backend = backend

    def check(self, device):
        if device != self.backend.device_path or time.monotonic() >= self.backend.pair_until:
            raise DBusError("org.bluez.Error.Rejected", "Kein Kopplungsfenster für diese Box")

    @method()
    def Release(self):
        pass

    @method()
    def Cancel(self):
        LOG.info("Pairing canceled")

    @method()
    def RequestAuthorization(self, device: 'o'):
        self.check(device)

    @method()
    def RequestConfirmation(self, device: 'o', passkey: 'u'):
        # No numeric-comparison UI is implemented; never silently confirm it.
        raise DBusError("org.bluez.Error.Rejected", "Numerische Bestätigung nicht unterstützt")

    @method()
    def RequestPinCode(self, device: 'o') -> 's':
        raise DBusError("org.bluez.Error.Rejected", "PIN-Kopplung nicht unterstützt")

    @method()
    def RequestPasskey(self, device: 'o') -> 'u':
        raise DBusError("org.bluez.Error.Rejected", "Passkey nicht unterstützt")

    @method()
    def AuthorizeService(self, device: 'o', uuid: 's'):
        self.check(device)

class BlueZ:
    def __init__(self, options):
        self.adapter = "/org/bluez/" + options["adapter"]
        self.address = options["box_address"].upper()
        if not re.fullmatch(r"(?:[0-9A-F]{2}:){5}[0-9A-F]{2}", self.address) or self.address == "00:00:00:00:00:00":
            raise ValueError("Bitte zuerst die Bluetooth-Adresse der eigenen iNet-Box konfigurieren.")
        self.device_path = self.adapter + "/dev_" + self.address.replace(":", "_")
        self.bus = None
        self.advertising = False
        self.registered = False
        self.agent_registered = False
        self.pair_until = 0
        self.original_pairable = False
        self.pair_task = None
        self.paths = {}
        self.flags = {}
        self.subscriptions = []
        self.wake = asyncio.Event()
        self.capabilities = {}
        self.restart_required = False

    async def call(self, path, interface, member, signature="", body=None, destination="org.bluez"):
        reply = await asyncio.wait_for(self.bus.call(Message(
            destination=destination, path=path, interface=interface, member=member,
            signature=signature, body=body or [])), 20)
        if reply.message_type == MessageType.ERROR:
            raise DBusError(reply.error_name, str(reply.body[0]) if reply.body else member)
        return reply.body

    async def objects(self):
        return plain((await self.call("/", OM, "GetManagedObjects"))[0])

    async def properties(self, path, interface):
        return plain((await self.call(path, PROPS, "GetAll", "s", [interface]))[0])

    async def set_property(self, path, interface, name, signature, value):
        await self.call(path, PROPS, "Set", "ssv", [interface, name, Variant(signature, value)])

    def signal(self, msg):
        if (msg.message_type == MessageType.SIGNAL and
                msg.interface == "org.freedesktop.DBus" and msg.member == "NameOwnerChanged" and
                msg.body and msg.body[0] == "org.bluez"):
            self.restart_required = True
            self.wake.set()
        if msg.message_type == MessageType.SIGNAL and msg.path and msg.path.startswith(self.device_path):
            self.wake.set()

    async def start(self):
        self.bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        self.bus.add_message_handler(self.signal)
        await self.call("/org/freedesktop/DBus", "org.freedesktop.DBus", "AddMatch", "s",
                        ["type='signal',sender='org.bluez'"], "org.freedesktop.DBus")
        await self.call("/org/freedesktop/DBus", "org.freedesktop.DBus", "AddMatch", "s",
                        ["type='signal',interface='org.freedesktop.DBus',member='NameOwnerChanged',arg0='org.bluez'"],
                        "org.freedesktop.DBus")
        objects = await self.objects()
        adapter = objects.get(self.adapter, {})
        self.capabilities = adapter.get("org.bluez.LEAdvertisingManager1", {})
        if "org.bluez.GattManager1" not in adapter or not self.capabilities:
            raise RuntimeError("Der Bluetooth-Adapter bietet keinen GATT-Server mit Advertising an.")
        if not adapter["org.bluez.Adapter1"].get("Powered"):
            raise RuntimeError("Bluetooth ist ausgeschaltet.")
        self.bus.export(ROOT, Application())
        self.bus.export(SERVICE, PhoneService())
        self.bus.export(CHAR, PhoneCharacteristic(self))
        self.bus.export(ADV, Advertisement())
        self.bus.export(AGENT, Agent(self))
        await self.call(self.adapter, "org.bluez.GattManager1", "RegisterApplication", "oa{sv}", [ROOT, {}])
        self.registered = True
        await self.advertise(True)
        LOG.info("GATT server and advertisement registered; waiting for %s", self.address)

    async def advertise(self, enabled):
        if enabled == self.advertising:
            return
        if enabled:
            await self.call(self.adapter, "org.bluez.LEAdvertisingManager1", "RegisterAdvertisement",
                            "oa{sv}", [ADV, {}])
        else:
            await self.call(self.adapter, "org.bluez.LEAdvertisingManager1", "UnregisterAdvertisement", "o", [ADV])
        self.advertising = enabled

    async def pair(self, seconds=120):
        if self.pair_until > time.monotonic():
            return
        props = await self.properties(self.adapter, "org.bluez.Adapter1")
        self.original_pairable = props["Pairable"]
        try:
            await self.call("/org/bluez", "org.bluez.AgentManager1", "RegisterAgent", "os", [AGENT, "NoInputNoOutput"])
            self.agent_registered = True
            self.pair_until = time.monotonic() + seconds
            await self.call("/org/bluez", "org.bluez.AgentManager1", "RequestDefaultAgent", "o", [AGENT])
            await self.set_property(self.adapter, "org.bluez.Adapter1", "Pairable", "b", True)
            await self.advertise(True)
            self.pair_task = asyncio.create_task(self.expire_pairing(seconds))
        except Exception:
            await self.close_pairing()
            raise

    async def expire_pairing(self, seconds):
        await asyncio.sleep(seconds)
        await self.close_pairing()

    async def close_pairing(self):
        self.pair_until = 0
        if self.pair_task and self.pair_task != asyncio.current_task():
            self.pair_task.cancel()
        self.pair_task = None
        if self.agent_registered:
            try:
                await self.set_property(self.adapter, "org.bluez.Adapter1", "Pairable", "b", self.original_pairable)
            finally:
                await self.call("/org/bluez", "org.bluez.AgentManager1", "UnregisterAgent", "o", [AGENT])
                self.agent_registered = False

    async def device(self):
        try:
            return await self.properties(self.device_path, DEVICE)
        except DBusError as exc:
            if exc.type in ("org.freedesktop.DBus.Error.UnknownObject", "org.freedesktop.DBus.Error.UnknownInterface",
                            "org.bluez.Error.DoesNotExist", "org.freedesktop.DBus.Error.InvalidArgs"):
                return {}
            raise

    async def discover(self):
        objects = await self.objects()
        services = {p for p, x in objects.items() if p.startswith(self.device_path + "/") and
                    x.get("org.bluez.GattService1", {}).get("UUID") == HEATER_SERVICE}
        if len(services) != 1:
            raise RuntimeError("Der erwartete Combi-Dienst wurde nicht eindeutig gefunden.")
        paths, flags = {}, {}
        inventory = []
        for path, interfaces in objects.items():
            if not path.startswith(self.device_path + "/") or GATT not in interfaces:
                continue
            char = interfaces[GATT]
            inventory.append({"path": path, "uuid": char["UUID"], "service": char["Service"], "flags": char["Flags"]})
            if char["Service"] not in services:
                continue
            for kind, uuid in CHARACTERISTICS.items():
                if char["UUID"] == uuid:
                    if kind in paths:
                        raise RuntimeError("Mehrdeutige Bluetooth-Characteristic")
                    paths[kind], flags[kind] = path, char["Flags"]
        if set(paths) != set(CHARACTERISTICS) or any("read" not in v for v in flags.values()):
            raise RuntimeError("Temperatur, Gebläse und Warmwasser sind noch nicht vollständig lesbar.")
        self.paths, self.flags = paths, flags
        for kind, uuid in MEASUREMENTS.items():
            matches = [c for c in inventory if c["uuid"].lower() == uuid and
                       objects.get(c["service"], {}).get("org.bluez.GattService1", {}).get("UUID", "").lower() == MEASUREMENT_SERVICE
                       and "read" in c["flags"]]
            if len(matches) == 1:
                self.paths[kind] = matches[0]["path"]
                self.flags[kind] = matches[0]["flags"]
        # Polling is the initial verified read path. Subscribe only to discovered
        # change-indication attributes in the vendor namespace, never fixed handles.
        for char in inventory:
            if char["uuid"].endswith("fe088214") and "indicate" in char["flags"]:
                try:
                    await self.call(char["path"], GATT, "StartNotify")
                    self.subscriptions.append(char["path"])
                except DBusError as exc:
                    LOG.warning("Change subscription unavailable: %s", exc.type)
        return inventory

    async def read(self, kind):
        return bytes((await self.call(self.paths[kind], GATT, "ReadValue", "a{sv}", [{}]))[0])

    async def trust_verified_box(self):
        props = await self.device()
        if not props.get("Paired") or not set(CHARACTERISTICS).issubset(self.paths):
            raise RuntimeError("Box noch nicht vollständig verifiziert")
        if not props.get("Trusted"):
            await self.set_property(self.device_path, DEVICE, "Trusted", "b", True)

    async def write(self, kind, payload):
        if kind not in CHARACTERISTICS:
            raise ValueError("Messwerte sind ausschließlich lesbar")
        if "write" not in self.flags.get(kind, []):
            raise RuntimeError("Schreiben mit Bestätigung wird von diesem Attribut nicht angeboten.")
        await self.call(self.paths[kind], GATT, "WriteValue", "aya{sv}", [payload, {"type": Variant("s", "request")}])

    async def measurements(self):
        result = dict.fromkeys(MEASUREMENTS)
        for kind in MEASUREMENTS:
            if kind not in self.paths:
                continue
            try:
                result[kind] = decode_measurement(kind, await asyncio.wait_for(self.read(kind), 2))
            except (DBusError, OSError, asyncio.TimeoutError) as exc:
                LOG.warning("Measurement %s unavailable: %s", kind, exc)
        return result

    async def disconnect(self):
        self.paths = {}
        self.flags = {}
        self.subscriptions = []
        props = await self.device()
        if props.get("Connected"):
            await self.call(self.device_path, DEVICE, "Disconnect")

    async def stop(self):
        if not self.bus:
            return
        try:
            if not self.restart_required:
                await self.close_pairing()
                await self.advertise(False)
                if self.registered:
                    await self.call(self.adapter, "org.bluez.GattManager1", "UnregisterApplication", "o", [ROOT])
        except DBusError as exc:
            if exc.type not in ("org.bluez.Error.DoesNotExist", "org.freedesktop.DBus.Error.UnknownObject",
                                "org.freedesktop.DBus.Error.ServiceUnknown"):
                raise
        finally:
            if self.pair_task:
                self.pair_task.cancel()
                self.pair_task = None
            self.bus.disconnect()
            self.bus = None

    async def restart(self):
        await self.stop()
        self.advertising = self.registered = self.agent_registered = False
        self.pair_until = 0
        self.paths, self.flags, self.subscriptions = {}, {}, []
        self.restart_required = True
        await self.start()
        self.restart_required = False
