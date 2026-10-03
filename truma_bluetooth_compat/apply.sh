#!/bin/sh
set -eu
dir=/run/systemd/system/bluetooth.service.d
file=$dir/90-truma-inet-timing.conf
if [ -e "$file" ] && ! grep -q '^# Managed by Truma Bluetooth Kompatibilität$' "$file"; then
    echo 'Existing override is not owned by this app; refusing to replace it.' >&2
    exit 1
fi
mkdir -p "$dir"
cat > "$file.tmp" <<'EOF'
# Managed by Truma Bluetooth Kompatibilität
[Service]
Environment=LD_PRELOAD=/mnt/data/supervisor/share/truma-inet-compat/security-delay.so
Environment=TRUMA_INET_ADDRESS=@TRUMA_ADDRESS@
EOF
mv "$file.tmp" "$file"
/usr/bin/systemctl daemon-reload
/usr/bin/systemctl restart bluetooth.service
