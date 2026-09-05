# UniFi Dashboard Telemetry 0.8.0-rc4

This release-candidate companion layer adds the telemetry contracts consumed by `Zabbix-UniFi-Dashboard` without changing the stable 0.7.0 production template while validation is completed.

## What it adds

- Per-client traffic ranking over a rolling 24-hour window from controller-local `GET /v2/api/site/<site>/traffic`.
- Current wireless client RSSI in dBm, AP, SSID and identity data from legacy `stat/sta`.
- Site-wide DPI application traffic from the same v2 traffic endpoint, with legacy `stat/sitedpi` retained as a compatibility fallback.
- DPI application-name enrichment from the Integration API `/v1/dpi/applications` catalog when a matching catalog identifier is available.
- Wi-Fi association, authentication, DHCP and DNS success metrics from controller-local `GET /v2/api/site/<site>/wifi-connectivity`.

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

Adjust ownership and mode to match the existing Zabbix installation. Import the companion template matching the Zabbix major version and link it to the same UniFi host that already uses `UniFi UDM Pro API Monitoring >= 0.7.0`.

The companion template deliberately does not redefine the API macros. It expects the host to already provide:

```text
{$UNIFI.API.URL}
{$UNIFI.API.KEY}
{$UNIFI.NETWORK.SITE}
```

`{$UNIFI.TLS.ARG}` is referenced for compatibility with the base template. Live validation on Zabbix 8.0 showed that a macro defined only on a sibling linked template can remain unresolved in the companion external-item command line. The collector therefore ignores only unresolved Zabbix macro tokens such as `{$UNIFI.TLS.ARG}`; normal values such as `--timeout=20` and `--verify-tls` are still honored.

## Traffic time window

UniFi Network 10.6.101 was verified to require `start` and `end` on the v2 `/traffic` endpoint in Unix epoch **milliseconds**. Sending epoch seconds returns HTTP 200 with empty `total_usage_by_app` and `client_usage_by_app` arrays. RC4 converts the collector's internal second-based rolling window to milliseconds only for the HTTP request and keeps the normalized output `start`/`end` values in seconds.

When usable v2 client traffic is returned, RC4 resets the legacy station traffic counters before applying v2 totals. This prevents mixing a 24-hour v2 window with legacy counters for clients not present in `client_usage_by_app`.

## DPI identifiers

The v2 traffic payload exposes separate numeric `category` and `application` values. RC4 converts them to UniFi's compound DPI identifier using `(category << 16) + application` before looking up the Integration API application catalog. Live validation confirmed that this mapping resolves real application names (for example SSL/TLS, Instagram, iCloud and YouTube) and avoids collisions where the same application number exists in more than one category.

## Manual collector tests

Use the same URL, API key and Network site configured in the base template. Do not paste the API key into tickets or logs.

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
{"available":true,"association":100.0,"authentication":100.0,"dhcp":100.0,"dns":100.0}
```

## Live validation notes

Validated on Zabbix 8.0.0beta2 with UniFi Network 10.6.101 / UniFi OS 5.1.31:

- `GET /proxy/network/v2/api/site/<site>/traffic` with epoch seconds returned HTTP 200 but empty traffic arrays.
- The same request with epoch milliseconds returned 74 `total_usage_by_app` entries and 29 `client_usage_by_app` entries over the tested 24-hour window.
- RC4 `clients` returned 33 normalized client records across the current station table and rolling traffic window, with 19 current wireless RSSI values and non-zero 24-hour Top Clients ranking.
- RC4 `dpi` returned 74 applications totaling 32,575,858,256 bytes in the tested 24-hour window. Compound DPI IDs resolved to catalog names correctly.
- The Integration API DPI catalog returned `totalCount: 2112` and application identifiers/names.
- `GET /proxy/network/v2/api/site/<site>/wifi-connectivity` returned live association, authentication, DHCP and DNS ratios plus total attempts, failed client connections and latency data. The latest tested sample returned 100% for all four stages with 392 attempts, zero failed client connections and 14 clients.
- Legacy `stat/sitedpi` returned an empty application set on the tested controller; RC4 therefore prefers the validated v2 traffic source and only uses the legacy endpoint as fallback.

## Validation checklist

1. `python3 -m py_compile unifi_dashboard_telemetry.py` succeeds.
2. `clients` reports `traffic_source: v2/traffic` and a non-zero rolling-window Top Clients ranking. **Validated.**
3. `dpi` reports `traffic_source: v2/traffic`, non-zero application traffic, and correct catalog name resolution. **Validated.**
4. `wifi-performance` reports `available:true` and the four connectivity success values. **Validated.**
5. The Zabbix LLD rules create `unifi.client.*`, `unifi.radio.rssi[*]`, and `unifi.dpi.app.*` items.
6. The UniFi Dashboard fills Top clients, Density / signal strength, Top applications and Wi-Fi Connectivity from those item contracts.

## Why this is a companion template first

The existing 0.7.0 template is already in production use. Keeping the new collection isolated as an RC makes rollback simple and prevents validation changes from destabilizing the stable template. After end-to-end Zabbix and dashboard validation, these items can be folded into the main 7.0/8.0 templates as the 0.8.0 release.
