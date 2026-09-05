# UniFi Dashboard Telemetry 0.8.0

Dashboard telemetry is part of the main `UniFi UDM Pro API Monitoring` template and collector. There is no companion template and no second production collector.

## Final layout

```text
UniFi UDM Pro API Monitoring/
├── 7.0/UniFi_UDM_Pro_API_Monitoring_7.0.yaml
├── 8.0/UniFi_UDM_Pro_API_Monitoring_8.0.yaml
├── unifi_udm_pro_api.py
├── README.md
├── README.pt-BR.md
├── CHANGELOG.md
├── CHANGELOG.pt-BR.md
└── docs/
```

Install exactly one external script: `unifi_udm_pro_api.py`. Import exactly one template for the Zabbix major version in use.

## API surfaces

The collector uses the documented Integration API together with controller-local Network API endpoints that were live-tested on UniFi Network 10.6.101 / UniFi OS 5.1.31.

- Integration API: `/proxy/network/integration/v1`
- Legacy operational API: `/proxy/network/api/s/<site>/...`
- Traffic: `/proxy/network/v2/api/site/<site>/traffic`
- Wi-Fi connectivity: `/proxy/network/v2/api/site/<site>/wifi-connectivity`

The v2 traffic endpoint requires `start` and `end` in Unix epoch milliseconds.

## Rolling dashboard windows

The unified template exposes four independent rolling traffic windows:

| Period | Seconds | Collection interval |
|---|---:|---:|
| 1h | 3600 | 2m |
| 1d | 86400 | 5m |
| 1w | 604800 | 15m |
| 1m | 2592000 | 1h |

Live collector tests returned the 1-week window in about 0.74 s and the 30-day window in about 1.00 s on the validated controller.

## Dashboard contracts

```text
unifi.client.name[<client-id>]
unifi.client.traffic.bytes[1h,<client-id>]
unifi.client.traffic.bytes[1d,<client-id>]
unifi.client.traffic.bytes[1w,<client-id>]
unifi.client.traffic.bytes[1m,<client-id>]

unifi.radio.rssi[<client-id>]

unifi.dpi.app.name[<compound-app-id>]
unifi.dpi.app.bytes[1h,<compound-app-id>]
unifi.dpi.app.bytes[1d,<compound-app-id>]
unifi.dpi.app.bytes[1w,<compound-app-id>]
unifi.dpi.app.bytes[1m,<compound-app-id>]

unifi.wifi.association.success
unifi.wifi.authentication.success
unifi.wifi.dhcp.success
unifi.wifi.dns.success
```

DPI application IDs use UniFi's compound identifier `(category << 16) + application`. The application catalog is read from the Integration API and was validated with 2,112 catalog entries.

## Collector commands used by the dashboard

```bash
./unifi_udm_pro_api.py version
./unifi_udm_pro_api.py dashboard-client-status "$UNIFI_API_URL" "$UNIFI_API_KEY" default --timeout=20
./unifi_udm_pro_api.py dashboard-traffic "$UNIFI_API_URL" "$UNIFI_API_KEY" default 3600 --timeout=20
./unifi_udm_pro_api.py dpi-catalog "$UNIFI_API_URL" "$UNIFI_API_KEY" default --timeout=20
./unifi_udm_pro_api.py wifi-connectivity "$UNIFI_API_URL" "$UNIFI_API_KEY" default --timeout=20
```

`dashboard-traffic` returns both per-client and per-application traffic from a single v2 traffic request for the requested window.

## Validated behavior

The unified collector was manually validated with 1h, 1d, 1w and 30d windows. Current client RSSI, the 2,112-entry DPI catalog and Wi-Fi association/authentication/DHCP/DNS metrics were also validated against the same controller.

The Zabbix Dashboard module 0.2 uses the period-aware item keys above. The older temporary one-argument traffic compatibility keys and the companion telemetry template are intentionally not part of the final 0.8 layout.
