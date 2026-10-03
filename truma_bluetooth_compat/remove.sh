#!/bin/sh
set -eu
file=/run/systemd/system/bluetooth.service.d/90-truma-inet-timing.conf
if [ ! -e "$file" ]; then exit 0; fi
if ! grep -q '^# Managed by Truma Bluetooth Kompatibilität$' "$file"; then
    echo 'Override ownership changed; refusing to remove it.' >&2
    exit 1
fi
rm "$file"
/usr/bin/systemctl daemon-reload
/usr/bin/systemctl restart bluetooth.service
