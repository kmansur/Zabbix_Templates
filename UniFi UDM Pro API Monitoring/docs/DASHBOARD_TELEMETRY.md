# UniFi Dashboard Telemetry 0.8.0-rc2

This release-candidate companion layer adds the telemetry contracts already consumed by `Zabbix-UniFi-Dashboard` without changing the stable 0.7.0 template while live validation is still in progress.

## What it adds

- Per-client traffic ranking from the legacy Network `stat/sta` endpoint.
- Wireless client RSSI in dBm from the same station payload.
- Site-wide DPI application traffic from legacy `stat/sitedpi` with `type=by_app`.
- DPI application names enriched from the documented Integration API `/v1/dpi/applications` catalog when available.
- Optional Wi-Fi connectivity metrics from the controller-local `/v2/api/site/<site>/wifi-stats/performance` endpoint.

The resulting Zabbix keys match the dashboard contracts:

```text
unifi.client.name[<client-id>]
unifi.client.traffic.bytes[<client-id>]
unifi.radio.rssi[<client-id>]
unifi.dpi.app.name[<app-id>]
unifi.dpi.app.bytes[<app-id>]
unifi.wifi.association.success
unifi.wifi.authentication.success
unifi.wifi.dhcp.success
unifi.wifi.dns.success
```

## Files

```text
unifi_dashboard_telemetry.py
7.0/UniFi_UDM_Pro_Dashboard_Telemetry_7.0.yaml
8.0/UniFi_UDM_Pro_Dashboard_Telemetry_8.0.yaml
```

## Installation for validation

Copy the collector to the same `ExternalScripts` directory that already contains `unifi_udm_pro_api.py`:

```bash
install -o root -g zabbix -m 0750 \
  unifi_dashboard_telemetry.py \
  /usr/lib/zabbix/externalscripts/unifi_dashboard_telemetry.py
```

Adjust the path and group to match the existing Zabbix installation.

Import the companion template matching the Zabbix major version and link it to the same UniFi host that already uses `UniFi UDM Pro API Monitoring >= 0.7.0`.

The companion template deliberately does not redefine the API macros. It expects the host to already provide:

```text
{$UNIFI.API.URL}
{$UNIFI.API.KEY}
{$UNIFI.NETWORK.SITE}
```

`{$UNIFI.TLS.ARG}` is also referenced for compatibility with the base template. During live validation on Zabbix 8.0 it was confirmed that a macro defined only on a sibling linked template can remain unresolved for the companion item's external-script command. Starting with rc2 the collector safely ignores only unresolved Zabbix macro tokens such as `{$UNIFI.TLS.ARG}` and falls back to its default timeout/TLS behavior. If the macro is defined directly on the host, normal values such as `--timeout=20` and `--verify-tls` are still honored.

## Manual collector tests

Use the same URL, API key and Network site already configured in the base template. Do not paste the API key into tickets or logs.

```bash
./unifi_dashboard_telemetry.py clients \
  "$UNIFI_API_URL" "$UNIFI_API_KEY" default --timeout=20

./unifi_dashboard_telemetry.py dpi \
  "$UNIFI_API_URL" "$UNIFI_API_KEY" default --timeout=20

./unifi_dashboard_telemetry.py wifi-performance \
  "$UNIFI_API_URL" "$UNIFI_API_KEY" default --timeout=20
```

Expected top-level shapes:

```json
{"clients":{},"summary":{}}
{"applications":{},"summary":{}}
{"available":true,"association":99.0,"authentication":99.0,"dhcp":99.0,"dns":99.0}
```

The Wi-Fi performance response is intentionally optional. UniFi's documented Integration API uses API-key authentication, while controller-local v2 endpoints can have different authentication behavior between releases. If the v2 endpoint rejects the API key or is absent, the collector returns `available:false` instead of fabricating success percentages.

## Validation checklist

1. `python3 -m py_compile unifi_dashboard_telemetry.py` succeeds.
2. `clients` returns active clients and negative dBm RSSI for wireless stations where exposed.
3. `dpi` returns one or more applications when Traffic Identification/DPI is enabled and the controller exposes site DPI statistics through the tested endpoint.
4. The Zabbix LLD rules create `unifi.client.*`, `unifi.radio.rssi[*]`, and `unifi.dpi.app.*` items.
5. The UniFi Dashboard fills Top clients, Density / signal strength and Top applications without dashboard code changes.
6. If `wifi-performance` returns `available:true`, the Wi-Fi Connectivity card also fills automatically.

## Live validation notes

Validated on Zabbix 8.0.0beta2 with UniFi Network 10.6.101:

- `stat/sta` returned 27 active clients, including 17 wireless stations with valid negative dBm RSSI values and per-client traffic counters.
- The initial rc1 master items failed because `{$UNIFI.TLS.ARG}` remained literal in the companion template command line. rc2 fixes this by ignoring unresolved Zabbix macro tokens only.
- `/proxy/network/v2/api/site/<site>/wifi-stats/performance` returned HTTP 404 on the tested Network 10.6.101 system, so Wi-Fi Connectivity remains optional pending identification of the controller's current internal source.
- `stat/sitedpi` with `type=by_app` returned an empty application set on the tested system; DPI collection remains under investigation.

## Why this is a companion template first

The existing 0.7.0 template is already in use. Client/RSSI and DPI collection use established legacy API families, but the Wi-Fi performance endpoint needs validation on the target Network 10.6.101 system. Keeping the new collection isolated as an RC makes rollback trivial and prevents a partially validated endpoint from destabilizing the production template.

After successful live validation, these items can be folded into the main 7.0/8.0 templates as the 0.8.0 release.
