#!/usr/bin/env python3
"""Conservative publication check. Never prints matched secret values."""
import ipaddress
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = set(['.github/ISSUE_TEMPLATE/bug_report.md', '.github/pull_request_template.md', '.github/workflows/tests.yml', '.gitignore', 'AI_DISCLOSURE.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'DEPENDENCIES.json', 'LEGAL.md', 'LICENSE', 'PROTOCOL.md', 'PUBLISHING.md', 'README.md', 'RELEASE_CHECKLIST.md', 'RELEASE_NOTES.md', 'SECURITY.md', 'THIRD_PARTY.md', 'VALIDATION.md', 'dashboard.json', 'dashboard/camper-inet-card.js', 'repository.yaml', 'tests/test_bluez_recovery.py', 'tests/test_bridge.py', 'tests/test_diagnostics.py', 'tests/test_measurements.py', 'tests/test_resilience.py', 'truma_bluetooth_compat/Dockerfile', 'truma_bluetooth_compat/LICENSE', 'truma_bluetooth_compat/README.md', 'truma_bluetooth_compat/apply.sh', 'truma_bluetooth_compat/config.json', 'truma_bluetooth_compat/main.py', 'truma_bluetooth_compat/remove.sh', 'truma_bluetooth_compat/tests/test_security_delay.c', 'truma_bluetooth_compat/truma_security_delay.c', 'truma_inet_bridge/Dockerfile', 'truma_inet_bridge/LICENSE', 'truma_inet_bridge/bridge/__init__.py', 'truma_inet_bridge/bridge/bluez.py', 'truma_inet_bridge/bridge/diagnostics.py', 'truma_inet_bridge/bridge/index.html', 'truma_inet_bridge/bridge/main.py', 'truma_inet_bridge/bridge/mqtt.py', 'truma_inet_bridge/bridge/protocol.py', 'truma_inet_bridge/config.json', 'truma_inet_bridge/requirements.txt', 'scripts/check_release.py'])
EXCLUDED_DIRS = {'.git', '__pycache__', '.venv', 'venv'}
SYNTHETIC_MACS = {'00:00:00:00:00:00', '00:11:22:33:44:55', '02:11:22:33:44:55'}
PATTERNS = {
    'private key': r'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----',
    'GitHub token': r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})',
    'JWT': r'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}',
    'personal filesystem path': r'(?:/Users/|/home/)[A-Za-z0-9_.-]+/',
    'SSH key': r'ssh-(?:ed25519|rsa)\s+AAAA[A-Za-z0-9+/=]{20,}',
    'credential in URL': r'https?://[^/\s:@]+:[^/\s@]+@',
}

def problems(name, data):
    found=[]
    if name not in ALLOWED: found.append('file not on reviewed allowlist')
    try: text=data.decode('utf-8')
    except UnicodeDecodeError: return found+['non-text content']
    for label, pattern in PATTERNS.items():
        if re.search(pattern,text): found.append(label)
    for value in re.findall(r'(?<![A-Fa-f0-9])(?:[A-Fa-f0-9]{2}:){5}[A-Fa-f0-9]{2}(?![A-Fa-f0-9])',text):
        if value.upper() not in SYNTHETIC_MACS: found.append('non-example device address')
    for value in re.findall(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])',text):
        try: ip=ipaddress.ip_address(value)
        except ValueError: continue
        # Supervisor ingress address is an intentional code trust boundary.
        if ip.is_private and value not in {'172.30.32.2','127.0.0.1','0.0.0.0'}:
            found.append('private network address')
    if name.endswith('/config.json'):
        try:
            options=json.loads(text).get('options',{})
            for key in ('box_address','mqtt_host','mqtt_username','mqtt_password','mqtt_ca'):
                if options.get(key): found.append('nonempty private default: '+key)
        except ValueError: found.append('invalid config JSON')
    return sorted(set(found))

def main():
    failures=[]; count=0
    for path in ROOT.rglob('*'):
        relative=path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in relative.parts): continue
        if path.is_symlink(): failures.append((str(relative),'symlink')); continue
        if not path.is_file(): continue
        count+=1
        failures.extend((str(relative),reason) for reason in problems(str(relative),path.read_bytes()))
    history=0
    if (ROOT/'.git').exists():
        result=subprocess.run(['git','rev-list','--objects','--all'],cwd=ROOT,capture_output=True,text=True,check=True)
        for line in result.stdout.splitlines():
            parts=line.split(' ',1)
            if len(parts)!=2: continue
            oid,name=parts
            kind=subprocess.run(['git','cat-file','-t',oid],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
            if kind!='blob':continue
            blob=subprocess.run(['git','cat-file','blob',oid],cwd=ROOT,capture_output=True,check=True).stdout
            history+=1
            failures.extend(('history:'+name,reason) for reason in problems(name,blob))
    if failures:
        for name,reason in failures: print(f'FAIL {name}: {reason}')
        return 1
    print(f'PASS: {count} reviewed text files; {history} reachable history blobs checked.')
    print('Pattern/allowlist check only: does not prove absence of every secret or third-party right.')
    return 0

if __name__=='__main__':sys.exit(main())
