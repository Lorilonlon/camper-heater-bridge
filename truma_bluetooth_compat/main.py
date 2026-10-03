import asyncio
import hashlib
import json
import re
import logging
from pathlib import Path
import shutil
import signal
import uuid
from dbus_next import BusType, Message, MessageType, Variant
from dbus_next.aio import MessageBus

LOG = logging.getLogger('truma-compat')
SHARE = Path('/share/truma-inet-compat')
HOST = '/mnt/data/supervisor/share/truma-inet-compat/'
UNIT = '/org/freedesktop/systemd1/unit/bluetooth_2eservice'
EXPECTED = 'LD_PRELOAD=' + HOST + 'security-delay.so'

async def call(bus, path, interface, member, signature='', body=None):
    reply = await asyncio.wait_for(bus.call(Message(destination='org.freedesktop.systemd1',
        path=path, interface=interface, member=member, signature=signature, body=body or [])), 30)
    if reply.message_type == MessageType.ERROR:
        raise RuntimeError(f'{reply.error_name}: {reply.body}')
    return reply.body

async def environment(bus):
    return (await call(bus, UNIT, 'org.freedesktop.DBus.Properties', 'Get',
        'ss', ['org.freedesktop.systemd1.Service', 'Environment']))[0].value

async def host_script(bus, script):
    name = 'truma-compat-' + uuid.uuid4().hex + '.service'
    manager = 'org.freedesktop.systemd1.Manager'
    await call(bus, '/org/freedesktop/systemd1', manager, 'StartTransientUnit', 'ssa(sv)a(sa(sv))',
        [name, 'fail', [['Type', Variant('s', 'oneshot')],
         ['RemainAfterExit', Variant('b', True)],
         ['TimeoutStartUSec', Variant('t', 30000000)],
         ['ExecStart', Variant('a(sasb)', [['/bin/sh', ['/bin/sh', HOST + script], False]])]], []])
    path = (await call(bus, '/org/freedesktop/systemd1', manager, 'GetUnit', 's', [name]))[0]
    try:
        for _ in range(70):
            state = (await call(bus, path, 'org.freedesktop.DBus.Properties', 'Get',
                'ss', ['org.freedesktop.systemd1.Unit', 'ActiveState']))[0].value
            if state == 'active':
                return
            if state == 'failed':
                raise RuntimeError('Bluetooth compatibility operation failed; inspect host journal')
            await asyncio.sleep(0.5)
        raise TimeoutError('Bluetooth compatibility operation timed out')
    finally:
        await call(bus, '/org/freedesktop/systemd1', manager, 'StopUnit', 'ss', [name, 'replace'])

async def main():
    address = json.loads(Path('/data/options.json').read_text()).get('box_address', '').upper()
    if not re.fullmatch(r'(?:[0-9A-F]{2}:){5}[0-9A-F]{2}', address) or address == '00:00:00:00:00:00':
        raise ValueError('Bitte zuerst die Bluetooth-Adresse der eigenen iNet-Box konfigurieren.')
    expected_address = 'TRUMA_INET_ADDRESS=' + address
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    stop = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_running_loop().add_signal_handler(sig, stop.set)
    installed = False
    try:
        env = await environment(bus)
        if any(x.startswith('LD_PRELOAD=') and x != EXPECTED for x in env):
            raise RuntimeError('Existing LD_PRELOAD setting belongs to another component; no changes made')
        SHARE.mkdir(parents=True, exist_ok=True)
        same_binary = (SHARE / 'security-delay.so').exists() and hashlib.sha256(
            (SHARE / 'security-delay.so').read_bytes()).digest() == hashlib.sha256(
            Path('/app/security-delay.so').read_bytes()).digest()
        for name in ('security-delay.so', 'apply.sh', 'remove.sh'):
            temp = SHARE / (name + '.tmp')
            if name == 'apply.sh':
                temp.write_text((Path('/app') / name).read_text().replace('@TRUMA_ADDRESS@', address))
            else:
                shutil.copyfile(Path('/app') / name, temp)
            temp.chmod(0o644)
            temp.replace(SHARE / name)
        if EXPECTED not in env or expected_address not in env or not same_binary:
            try:
                await host_script(bus, 'apply.sh')
            except Exception:
                await host_script(bus, 'remove.sh')
                raise
        installed = True
        active_env = await environment(bus)
        if EXPECTED not in active_env or expected_address not in active_env:
            raise RuntimeError('Bluetooth compatibility setting was not activated')
        LOG.info('Truma timing compatibility active; encryption policy unchanged')
        await stop.wait()
    finally:
        if installed:
            await host_script(bus, 'remove.sh')
            LOG.info('Original Bluetooth service configuration restored')
        bus.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
