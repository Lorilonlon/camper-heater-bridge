import unittest,tempfile
from pathlib import Path
from unittest.mock import AsyncMock
from bridge.protocol import decode_measurement,MEASUREMENTS,MEASUREMENT_SERVICE,CHARACTERISTICS,HEATER_SERVICE
from bridge.bluez import BlueZ,GATT
from bridge.main import Bridge
from test_bridge import FakeBackend

class MeasurementTests(unittest.IsolatedAsyncioTestCase):
    def test_capture_values(self):
        self.assertEqual(decode_measurement('current_temperature',bytes.fromhex('bc0b')),27.4)
        self.assertEqual(decode_measurement('voltage',bytes.fromhex('8300')),13.1)
        self.assertEqual(decode_measurement('voltage',bytes.fromhex('8400')),13.2)
    def test_water_live_value_and_range(self):
        self.assertEqual(decode_measurement('water_temperature',bytes.fromhex('340d')),65)
        self.assertEqual(decode_measurement('water_temperature',(2730).to_bytes(2,'little')),0)
        self.assertIsNone(decode_measurement('water_temperature',(4000).to_bytes(2,'little')))
        self.assertIsNone(decode_measurement('water_temperature',(2680).to_bytes(2,'little')))
    def test_negative_and_missing_values(self):
        self.assertEqual(decode_measurement('current_temperature',(2680).to_bytes(2,'little')),-5)
        for kind in MEASUREMENTS:
            for raw in (b'',b'\0',b'\0\0',b'\xff\xff',b'\x01\x02\x03'):
                self.assertIsNone(decode_measurement(kind,raw))
        self.assertIsNone(decode_measurement('voltage',(5000).to_bytes(2,'little')))
    async def test_measurements_never_writable(self):
        b=BlueZ({'adapter':'hci0','box_address':'00:11:22:33:44:55'})
        for kind in MEASUREMENTS:
            b.flags[kind]=['read','write']
            with self.assertRaises(ValueError):await b.write(kind,b'\x01\0')
    async def test_missing_or_failed_measurement_does_not_invent_zero(self):
        b=BlueZ({'adapter':'hci0','box_address':'00:11:22:33:44:55'})
        self.assertEqual(await b.measurements(),dict.fromkeys(MEASUREMENTS))
        b.paths={'current_temperature':'test','voltage':'test2'}
        b.read=AsyncMock(side_effect=[OSError('read failed'),bytes.fromhex('8400')])
        self.assertEqual(await b.measurements(),{'current_temperature':None,'voltage':13.2,'water_temperature':None})
    async def test_snapshot_and_commands_keep_measurements_separate(self):
        with tempfile.TemporaryDirectory() as d:
            backend=FakeBackend()
            backend.measurements=AsyncMock(return_value={'current_temperature':29.6,'voltage':13.2})
            bridge=Bridge({'allow_control':True},Path(d),backend)
            await bridge.snapshot()
            self.assertEqual(bridge.state['current_temperature'],29.6)
            polled = bridge.last_read
            await bridge.command('temperature','21',0)
            self.assertEqual(bridge.state['target'],21)
            self.assertEqual(bridge.state['current_temperature'],29.6)
            backend.measurements.assert_awaited_once()
            self.assertEqual(bridge.last_read,polled)
    async def test_optional_discovery_uses_service_and_uuid(self):
        b=BlueZ({'adapter':'hci0','box_address':'00:11:22:33:44:55'})
        hs=b.device_path+'/heat';ms=b.device_path+'/sensors'
        objects={hs:{'org.bluez.GattService1':{'UUID':HEATER_SERVICE}},ms:{'org.bluez.GattService1':{'UUID':MEASUREMENT_SERVICE}}}
        for kind,uuid in {**CHARACTERISTICS,**MEASUREMENTS}.items():
            service=ms if kind in MEASUREMENTS else hs
            objects[service+'/'+kind]={GATT:{'UUID':uuid,'Service':service,'Flags':['read']}}
        b.objects=AsyncMock(return_value=objects)
        await b.discover()
        self.assertEqual(b.paths['voltage'],ms+'/voltage')
        b.device=AsyncMock(return_value={'Paired':True,'Trusted':True})
        await b.trust_verified_box()
