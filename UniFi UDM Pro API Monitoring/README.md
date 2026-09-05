# UniFi UDM Pro API Monitoring for Zabbix

Unified UniFi Network monitoring for Zabbix 7.0 and 8.0.

Version: **0.8.0**  
Author: **Karim Mansur / Net Tech**

## What to install

The 0.8 release has one template and one external collector. There is no dashboard companion template and no second telemetry script.

```text
UniFi UDM Pro API Monitoring/
├── 7.0/UniFi_UDM_Pro_API_Monitoring_7.0.yaml
├── 8.0/UniFi_UDM_Pro_API_Monitoring_8.0.yaml
└── unifi_udm_pro_api.py
```

Choose the YAML matching the Zabbix major version and install `unifi_udm_pro_api.py` in the Zabbix `ExternalScripts` directory.

Example on Debian:

```bash
install -o root -g zabbix -m 0750 \
  unifi_udm_pro_api.py \
  /usr/lib/zabbix/externalscripts/unifi_udm_pro_api.py
```

Then import the template and link it to the UniFi host.

## UniFi API key

Create a local Network API key under **UniFi Network > Integrations**. The tested local base URL is:

```text
https://<gateway>/proxy/network/integration/v1
```

The collector also uses controller-local Network API endpoints for operational telemetry that is not exposed by the Integration API.

## Required macros

Configure the template/host macros as appropriate for the controller:

```text
{$UNIFI.API.URL}
{$UNIFI.API.KEY}
{$UNIFI.SITE.ID}
{$UNIFI.NETWORK.SITE}
{$UNIFI.TLS.ARG}
```

`{$UNIFI.SITE.ID}` is the Integration API site UUID when required by documented endpoints. `{$UNIFI.NETWORK.SITE}` is the internal Network site reference, normally `default` on a single-site UDM.

`{$UNIFI.TLS.ARG}` defaults to `--timeout=20`. Use `--verify-tls` when the gateway certificate is trusted by the Zabbix server.

## Dashboard telemetry

The main template now includes the data contracts required by `Zabbix-UniFi-Dashboard`.

Rolling traffic windows:

| Dashboard period | Window | Collection interval |
|---|---:|---:|
| 1h | 3600 s | 2m |
| 1D | 86400 s | 5m |
| 1S / 1W | 604800 s | 15m |
| 1M | 2592000 s (30 days) | 1h |

Client ranking keys:

```text
unifi.client.traffic.bytes[1h,<id>]
unifi.client.traffic.bytes[1d,<id>]
unifi.client.traffic.bytes[1w,<id>]
unifi.client.traffic.bytes[1m,<id>]
```

DPI ranking keys:

```text
unifi.dpi.app.bytes[1h,<id>]
unifi.dpi.app.bytes[1d,<id>]
unifi.dpi.app.bytes[1w,<id>]
unifi.dpi.app.bytes[1m,<id>]
```

Current Wi-Fi client signal and connectivity:

```text
unifi.radio.rssi[<client-id>]
unifi.wifi.association.success
unifi.wifi.authentication.success
unifi.wifi.dhcp.success
unifi.wifi.dns.success
```

## Unified collector commands

The collector preserves the existing 0.7 commands and adds the dashboard commands below:

```bash
./unifi_udm_pro_api.py version
./unifi_udm_pro_api.py dashboard-client-status URL API_KEY default --timeout=20
./unifi_udm_pro_api.py dashboard-traffic URL API_KEY default 3600 --timeout=20
./unifi_udm_pro_api.py dpi-catalog URL API_KEY default --timeout=20
./unifi_udm_pro_api.py wifi-connectivity URL API_KEY default --timeout=20
```

`dashboard-traffic` returns client and DPI application traffic from one controller v2 request for the selected rolling window.

## API surfaces used

- Integration API: `/proxy/network/integration/v1`
- Legacy operational API: `/proxy/network/api/s/<site>/...`
- Traffic: `/proxy/network/v2/api/site/<site>/traffic`
- Wi-Fi connectivity: `/proxy/network/v2/api/site/<site>/wifi-connectivity`

UniFi Network 10.6.101 was verified to require traffic `start` and `end` timestamps in Unix epoch **milliseconds**.

DPI application IDs use UniFi's compound form `(category << 16) + application` and names are resolved from the Integration API DPI catalog.

## Validation

Live validation was performed with UniFi Network **10.6.101**, UniFi OS **5.1.31** and Zabbix **8.0.0beta2**.

Validated collector windows and approximate controller response times:

- 1h: working
- 1d: working
- 1w: ~0.74 s
- 30d: ~1.00 s

The same environment validated current client RSSI, a 2,112-entry DPI catalog and Wi-Fi association/authentication/DHCP/DNS telemetry.

See `docs/DASHBOARD_TELEMETRY.md` and `docs/VALIDATION.md` for additional details.
