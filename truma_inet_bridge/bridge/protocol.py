"""Payloads derived from the user's 2026-09-22 Android HCI capture.

No fixed ATT handles: discovery must match the service and characteristic UUID.
5..30 C interpolation follows the app's integer temperature encoding; only 19,
30 and off have capture confirmation. Burner activity is not inferred.
"""
import math

ADVERTISED_UUID = "61808880-b7b3-11e4-b3a4-0002a5d5c51b"
PHONE_SERVICE = "73a58d00-c5a1-4f8e-8f55-1def871ddc81"
PHONE_CHARACTERISTIC = "73a58d01-c5a1-4f8e-8f55-1def871ddc81"
HEATER_SERVICE = "00010000-0004-0001-0000-0000fe088214"
MEASUREMENT_SERVICE = "00000000-0003-0001-0000-0000fe088214"
MEASUREMENTS = {
    "current_temperature": "00000001-0003-0001-0000-0000fe088214",
    "voltage": "00000004-0003-0001-0000-0000fe088214",
    "water_temperature": "00000003-0003-0001-0000-0000fe088214",
}

def decode_measurement(kind, payload):
    if len(payload) != 2:
        return None
    raw = int.from_bytes(payload, "little")
    if raw in (0, 65535):
        return None
    if kind == "current_temperature":
        value = round(raw / 10 - 273, 1)
        return value if -40 <= value <= 85 else None
    if kind == "water_temperature":
        value = round(raw / 10 - 273, 1)
        return value if 0 <= value <= 100 else None
    if kind == "voltage":
        value = round(raw / 10, 1)
        return value if 0 < value <= 40 else None
    raise ValueError("Unbekannter Messwert")

CHARACTERISTICS = {
    "temperature": "00010001-0004-0001-0000-0000fe088214",
    "fan": "00010002-0004-0001-0000-0000fe088214",
    "water": "00010004-0004-0001-0000-0000fe088214",
}
FANS = {0: "Aus", 1: "Eco", 10: "High"}
# Original APK: supported_tin_devices.json, Combi 6 EU/UK/US,
# capabilities.waterTemperature. Boost is an enum sentinel, not a water temperature.
WATER = {0: "Aus", 3130: "Niedrig", 3330: "Hoch", 4730: "Boost"}

def encode_temperature(value):
    n = float(value)
    if not math.isfinite(n) or not n.is_integer() or not 5 <= n <= 30:
        raise ValueError("Die Solltemperatur muss eine ganze Zahl zwischen 5 und 30 °C sein.")
    return ((int(n) + 273) * 10).to_bytes(2, "little")

def decode_temperature(payload):
    if len(payload) != 2:
        raise ValueError("Ungültige Länge der Solltemperatur")
    raw = int.from_bytes(payload, "little")
    if raw == 0:
        return None
    n = raw / 10 - 273
    if not 5 <= n <= 30 or not n.is_integer():
        raise ValueError("Unbekannter Solltemperaturwert")
    return int(n)

def decode_choice(payload, choices):
    if len(payload) not in (1, 2):
        raise ValueError("Ungültige Länge des Betriebsmodus")
    return choices.get(int.from_bytes(payload, "little"), "Unbekannt")

def command_writes(kind, value, state):
    """Build an explicit command, never replay it after reconnect."""
    if kind == "temperature":
        return [("temperature", encode_temperature(value))]
    if kind == "mode":
        if value == "off":
            # This exact two-write order was captured from the app.
            return [("fan", b"\x00"), ("temperature", b"\x00\x00")]
        if value == "heat":
            target = state.get("target")
            if target is None:
                raise ValueError("Bitte zuerst eine Solltemperatur auswählen.")
            # Composition of confirmed individual commands, needs hardware test.
            return [("fan", b"\x01"), ("temperature", encode_temperature(target))]
        raise ValueError("Unbekannter Heizmodus")
    if kind == "fan":
        values = {"Eco": b"\x01", "High": b"\x0a"}
        if value not in values:
            raise ValueError("Unbekannter Gebläsemodus")
        return [("fan", values[value])]
    if kind == "water":
        values = {label: raw.to_bytes(2, "little") for raw, label in WATER.items()}
        if value not in values:
            raise ValueError("Unbekannter Warmwassermodus")
        return [("water", values[value])]
    raise ValueError("Unbekannter Befehl")

def validate_write_reply(expected, actual):
    return (len(actual) in (1, 2) and int.from_bytes(actual, "little") ==
            int.from_bytes(expected, "little"))
