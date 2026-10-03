import unittest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from dbus_next import MessageType
from bridge.bluez import BlueZ

class RecoveryTests(unittest.IsolatedAsyncioTestCase):
    def backend(self):
        return BlueZ({'adapter':'hci0','box_address':'02:11:22:33:44:55'})

    async def test_only_bluez_owner_change_requires_recovery(self):
        backend = self.backend()
        event = SimpleNamespace(message_type=MessageType.SIGNAL,
            interface='org.freedesktop.DBus',member='NameOwnerChanged',
            body=['org.example.Other',':1.3',''],path='/org/freedesktop/DBus')
        backend.signal(event)
        self.assertFalse(backend.restart_required)
        event.body[0] = 'org.bluez'
        backend.signal(event)
        self.assertTrue(backend.restart_required)

    async def test_restart_forgets_stale_gatt_state_and_retries_failed_registration(self):
        backend = self.backend()
        backend.registered = backend.advertising = True
        backend.paths = {'temperature':'old-path'}
        backend.stop = AsyncMock()
        backend.start = AsyncMock(side_effect=RuntimeError('daemon not ready'))
        with self.assertRaises(RuntimeError):
            await backend.restart()
        self.assertTrue(backend.restart_required)
        self.assertFalse(backend.registered)
        self.assertEqual(backend.paths,{})
        backend.start = AsyncMock()
        await backend.restart()
        self.assertFalse(backend.restart_required)
        self.assertEqual(backend.stop.await_count,2)
