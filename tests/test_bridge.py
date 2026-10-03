import asyncio
import tempfile
import unittest
from pathlib import Path
from bridge.protocol import encode_temperature, decode_temperature, command_writes, validate_write_reply
from bridge.main import Bridge
from bridge.mqtt import MQTT
from types import SimpleNamespace

class FakeBackend:
    def __init__(self):
        self.values = {"temperature": bytes.fromhex("680b"), "fan": b"\x01\x00", "water": bytes.fromhex("3a0c")}
        self.writes = []
        self.connected = True
        self.fail_read = False
        self.mismatch = False
    async def device(self):
        return {"Connected": self.connected, "Paired": True, "ServicesResolved": True}
    async def read(self, k):
        if self.fail_read:
            raise OSError("Verbindung unterbrochen")
        return self.values[k]
    async def write(self, k, payload):
        self.writes.append((k, payload))
        if not self.mismatch:
            self.values[k] = payload

class ProtocolTests(unittest.TestCase):
    def test_capture_temperatures(self):
        for t, h in [(19,"680b"), (30,"d60b")]:
            self.assertEqual(encode_temperature(t).hex(), h)
            self.assertEqual(decode_temperature(bytes.fromhex(h)), t)
        self.assertIsNone(decode_temperature(b"\0\0"))
    def test_invalid_commands(self):
        for value in [float('nan'), float('inf'), -273, 0, 31, 20.5, 'oops']:
            with self.assertRaises((ValueError, TypeError)):
                encode_temperature(value)
    def test_invalid_read_not_fake_temperature(self):
        for value in [b'', b'\0', b'\xff\xff', b'\0\0\0']:
            with self.assertRaises(ValueError):
                decode_temperature(value)
    def test_off_capture_order(self):
        self.assertEqual(command_writes('mode','off',{}), [('fan',b'\0'),('temperature',b'\0\0')])
    def test_water_values_from_original_app(self):
        from bridge.protocol import WATER, decode_choice
        for label, payload in [('Aus','0000'),('Niedrig','3a0c'),('Hoch','020d'),('Boost','7a12')]:
            with self.subTest(label=label):
                raw = bytes.fromhex(payload)
                self.assertEqual(command_writes('water',label,{}), [('water',raw)])
                self.assertEqual(decode_choice(raw,WATER),label)
    def test_unknown_water_commands_blocked(self):
        for value in ['200','4730','Turbo',None]:
            with self.assertRaises(ValueError):
                command_writes('water',value,{})
    def test_fan_readback_is_two_bytes(self):
        self.assertTrue(validate_write_reply(b'\x0a',b'\x0a\0'))
        self.assertFalse(validate_write_reply(b'\x0a',b'\x01\0'))
    def test_heat_without_target_rejected(self):
        with self.assertRaises(ValueError):
            command_writes('mode','heat',{'target':None})

class BridgeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.backend = FakeBackend()
        self.bridge = Bridge({'allow_control':True},Path(self.tmp.name),self.backend)
        await self.bridge.snapshot()
    async def asyncTearDown(self):
        self.tmp.cleanup()
    async def test_read_only_blocks_write(self):
        self.bridge.options['allow_control']=False
        await self.bridge.command('temperature','30',0)
        self.assertEqual(self.backend.writes,[])

    async def test_stale_connection_command_dropped(self):
        self.bridge.generation=2
        await self.bridge.command('temperature','30',1)
        self.assertEqual(self.backend.writes,[])
    async def test_disconnected_command_dropped(self):
        self.backend.connected=False
        await self.bridge.command('temperature','30',0)
        self.assertEqual(self.backend.writes,[])
    async def test_confirmed_temperature(self):
        await self.bridge.command('temperature','30',0)
        self.assertEqual(self.bridge.state['target'],30)
        self.assertTrue(self.bridge.ready)
    async def test_off_temperature_only_stored_and_survives_restart(self):
        self.backend.values['temperature'] = b'\0\0'
        self.backend.values['fan'] = b'\0\0'
        # The command must re-read the box even if the last snapshot said heat.
        await self.bridge.command('temperature','22',0)
        self.assertEqual(self.backend.writes,[])
        self.assertEqual(self.bridge.state['mode'],'off')
        self.assertEqual(self.bridge.state['target'],22)
        again=Bridge({'allow_control':True},Path(self.tmp.name),self.backend)
        await again.snapshot()
        self.assertEqual(again.state['mode'],'off')
        self.assertEqual(again.state['target'],22)
        await again.command('mode','heat',0)
        self.assertEqual(self.backend.writes,[('fan',b'\x01'),('temperature',encode_temperature(22))])
        self.assertEqual(again.state['mode'],'heat')
    async def test_invalid_off_temperature_does_not_change_preset(self):
        self.backend.values['temperature'] = b'\0\0'
        await self.bridge.command('temperature','31',0)
        self.assertEqual(self.backend.writes,[])
        self.assertEqual(self.bridge.last_target,19)
    async def test_off_preset_preserves_water(self):
        self.backend.values['temperature'] = b'\0\0'
        for value in ('20','18','23'):
            await self.bridge.command('temperature',value,0)
            await self.bridge.snapshot()
            self.assertEqual(self.bridge.state['mode'],'off')
            self.assertEqual(self.bridge.state['target'],int(value))
            self.assertEqual(self.bridge.state['water'],'Niedrig')
        self.assertEqual(self.backend.writes,[])
    async def test_water_boost_and_off_preserve_heating(self):
        original = {k:self.bridge.state[k] for k in ('mode','target','fan')}
        for mode in ('Boost','Aus'):
            await self.bridge.command('water',mode,0)
            self.assertTrue(self.bridge.ready)
            self.assertEqual(self.bridge.state['water'],mode)
            self.assertEqual({k:self.bridge.state[k] for k in original},original)
        self.assertEqual(self.backend.writes,[('water',bytes.fromhex('7a12')),('water',bytes.fromhex('0000'))])
    async def test_unconfirmed_boost_is_not_published_as_success(self):
        self.backend.mismatch=True
        await self.bridge.command('water','Boost',0)
        self.assertFalse(self.bridge.ready)
        self.assertEqual(self.bridge.state['water'],'Niedrig')
    async def test_off_retains_confirmed_target_without_claiming_heat(self):
        await self.bridge.command('mode','off',0)
        self.assertEqual(self.bridge.state['mode'],'off')
        self.assertEqual(self.bridge.state['target'],19)
        again=Bridge({'allow_control':True},Path(self.tmp.name),self.backend)
        await again.snapshot()
        self.assertEqual(again.state['mode'],'off')
        self.assertEqual(again.state['target'],19)
    async def test_mismatch_not_optimistically_confirmed(self):
        self.backend.mismatch=True
        await self.bridge.command('temperature','30',0)
        self.assertFalse(self.bridge.ready)
        self.assertNotEqual(self.bridge.state['target'],30)
    async def test_partial_off_invalidates_state(self):
        original=self.backend.write
        async def fail_second(k,payload):
            if k=='temperature':raise OSError('disconnected')
            await original(k,payload)
        self.backend.write=fail_second
        await self.bridge.command('mode','off',0)
        self.assertFalse(self.bridge.ready)
        self.assertEqual(len(self.backend.writes),1)
    async def test_fresh_read_failure_prevents_write(self):
        self.backend.fail_read=True
        await self.bridge.command('temperature','30',0)
        self.assertFalse(self.bridge.ready)
        self.assertEqual(self.backend.writes,[])

    async def test_combined_ha_mode_and_temperature_are_serialized(self):
        self.bridge.schedule_command('mode','heat',0)
        self.bridge.schedule_command('temperature','30',0)
        await asyncio.gather(*self.bridge.command_tasks)
        self.assertEqual(self.bridge.state['target'],30)
        self.assertEqual(self.bridge.state['mode'],'heat')
        self.assertEqual(self.bridge.state['fan'],'Eco')

    async def test_expired_command_never_written(self):
        import time
        await self.bridge.command('temperature','30',0,time.monotonic()-10)
        self.assertEqual(self.backend.writes,[])

class MQTTTests(unittest.IsolatedAsyncioTestCase):
    async def test_retained_command_never_scheduled(self):
        scheduled=[]
        b=SimpleNamespace(generation=4,schedule_command=lambda *args:scheduled.append(args))
        transport=MQTT(b,{'box_address':'02:11:22:33:44:55'})
        transport.on_message(None,None,SimpleNamespace(topic=transport.base+'/set/mode',payload=b'heat',retain=True))
        await asyncio.sleep(0)
        self.assertEqual(scheduled,[])

    async def test_live_command_carries_connection_generation(self):
        scheduled=[]
        b=SimpleNamespace(generation=4,schedule_command=lambda *args:scheduled.append(args))
        transport=MQTT(b,{'box_address':'02:11:22:33:44:55'})
        transport.on_message(None,None,SimpleNamespace(topic=transport.base+'/set/mode',payload=b'off',retain=False))
        await asyncio.sleep(0)
        self.assertEqual(scheduled,[('mode','off',4)])

if __name__=='__main__':unittest.main()
