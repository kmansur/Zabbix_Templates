#!/usr/bin/env python3
from pathlib import Path

ROOT = Path('UniFi UDM Pro API Monitoring')
bs = '\\'

commands = [
    'https://<udm-pro-ip>/proxy/network/integration/v1/info',
    'https://<udm-pro-ip>/proxy/network/integration/v1/sites',
    'https://<udm-pro-ip>/proxy/network/integration/v1/sites/<site-id>/devices',
    'https://<udm-pro-ip>/proxy/network/integration/v1/sites/<site-id>/devices/<device-id>/statistics/latest',
]

for filename in ('README.md', 'README.pt-BR.md'):
    path = ROOT / filename
    text = path.read_text(encoding='utf-8')
    for url in commands:
        old = f'curl --fail-with-body -sS -k   -H "Accept: application/json"   -H "X-API-KEY: <api-key>"   "{url}"'
        new = (
            f'curl --fail-with-body -sS -k {bs}\n'
            f'  -H "Accept: application/json" {bs}\n'
            f'  -H "X-API-KEY: <api-key>" {bs}\n'
            f'  "{url}"'
        )
        if old not in text:
            raise SystemExit(f'missing curl formatting anchor in {filename}: {url}')
        text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')

print('README curl examples formatted')
