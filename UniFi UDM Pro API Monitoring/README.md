# UniFi UDM Pro API Monitoring

> Development status: this template is currently under active development and
> should be validated in a test host before production use.

Zabbix template project for monitoring a Ubiquiti UniFi Dream Machine Pro
through the UniFi Network API, Site Manager API, CEF/syslog events, and
optional NetFlow/IPFIX data.

## Goals

- Discover UniFi sites, devices, networks, clients, WAN links, and gateway data.
- Collect gateway health, WAN latency, packet loss, uptime, traffic, and device state.
- Use UniFi logs and CEF exports for operational and security events.
- Keep SNMP as an optional fallback for basic interface counters.

## Planned Sources

- Local Network API: `https://<udm-pro>/proxy/network/integration/v1`
- Site Manager API: `https://api.ui.com/v1`
- UniFi System Logs / SIEM CEF export
- Traffic Flows / NetFlow/IPFIX

## Creating API Keys

This project can use two different API keys. The local UniFi Network API key is
the primary key for monitoring a UDM Pro on the LAN. The Site Manager API key is
optional and is used when you want cloud-based or multi-site data from
`api.ui.com`.

### Local UniFi Network API Key

Use this key for direct access to the UDM Pro, for example:

```text
https://<udm-pro-ip>/proxy/network/integration/v1
```

Recommended process:

1. Log in to the UDM Pro web interface with an administrator account.
2. Open the UniFi Network application.
3. Go to **Settings**.
4. Open **Control Plane**.
5. Open **Integrations**.
6. Find the **API Keys** or **Network API** section.
7. Create a new API key.
8. Give the key a clear name, for example:

   ```text
   zabbix-udm-pro-monitoring
   ```

9. If UniFi offers an expiration option, choose the policy that matches your
   environment. For production monitoring, a non-expiring key is convenient, but
   a rotating key policy is safer.
10. Copy the generated key immediately and store it in the Zabbix secret macro
    or in the script environment. UniFi may not show the full key again.
11. Test the key from the Zabbix server or proxy:

    ```bash
    curl -k \
      -H "Accept: application/json" \
      -H "X-API-KEY: <api-key>" \
      "https://<udm-pro-ip>/proxy/network/integration/v1/sites"
    ```

Expected result: a JSON response with the available UniFi site or sites. On a
typical UDM Pro deployment, there will usually be one site.

After listing sites, use the returned site ID to test devices:

```bash
curl -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/sites/<site-id>/devices"
```

And clients:

```bash
curl -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/sites/<site-id>/clients"
```

### Site Manager API Key

Use this key only when the template needs cloud data from UniFi Site Manager,
such as multi-site inventory or ISP metrics from:

```text
https://api.ui.com/v1
```

Recommended process:

1. Go to the UniFi developer or Site Manager API area associated with your UI
   account.
2. Create an API key for the account that owns or administers the UDM Pro.
3. Give the key a clear name, for example:

   ```text
   zabbix-unifi-site-manager
   ```

4. Copy the key immediately and store it securely.
5. Test the key:

   ```bash
   curl \
     -H "Accept: application/json" \
     -H "X-API-Key: <api-key>" \
     "https://api.ui.com/v1/sites"
   ```

6. Test ISP metrics if you plan to use WAN history from Site Manager:

   ```bash
   curl \
     -H "Accept: application/json" \
     -H "X-API-Key: <api-key>" \
     "https://api.ui.com/ea/isp-metrics/5m?duration=24h"
   ```

### Security Recommendations

- Create a dedicated admin or service account for monitoring when possible.
- Grant only the minimum permissions required for read-only monitoring.
- Never hardcode API keys in scripts, templates, or Git-tracked files.
- Store the local key in a Zabbix secret macro, for example:

  ```text
  {$UNIFI.API.KEY}
  ```

- Store the UDM Pro URL in a regular macro, for example:

  ```text
  {$UNIFI.API.URL}
  ```

- Restrict API access at the firewall so only the Zabbix server or Zabbix proxy
  can reach the UDM Pro management interface.
- Prefer HTTPS with valid certificates where possible. If the UDM Pro uses a
  self-signed certificate, testing with `curl -k` is acceptable on a trusted LAN,
  but production scripts should make this behavior explicit and documented.
- Rotate the key after staff changes, suspected exposure, or repository leaks.
- Revoke old keys that are no longer used.

## Planned Zabbix Components

- Low-level discovery for devices, clients, networks, WAN links, and interfaces.
- HTTP/API items for UniFi Network and Site Manager metrics.
- Dependent items for JSON parsing.
- Trigger prototypes for WAN degradation, device offline, packet loss, high latency,
  firmware updates, and security events.
- Optional syslog trapper items for CEF events.

## Zabbix Template

Current project version:

```text
0.6.0
```

The importable Zabbix 7.0 template is:

```text
UniFi UDM Pro API Monitoring.yaml
```

Before importing or enabling the template:

1. Install `unifi_udm_pro_api.py` on the Zabbix server or proxy.
2. Import `UniFi UDM Pro API Monitoring.yaml`.
3. Link the template to the UDM Pro host.
4. Set host macros:

   ```text
   {$UNIFI.API.URL} = https://xxx.xxx.xxx.xxx
   {$UNIFI.API.KEY} = your local UniFi Network API key
   {$UNIFI.SITE.ID} = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   {$UNIFI.LEGACY.SITE} = default
   ```

`{$UNIFI.SITE.ID}` can be left empty when the controller has only one site. The
script will discover it automatically.
Fixed system and WAN items auto-select the UDM device from the legacy payload.
Do not set a device ID macro for normal template use; explicit legacy device
IDs are only needed for manual script tests.

The initial template includes:

- UniFi Network application version.
- Device summary: total, online, offline, firmware updates available.
- Client summary: total, wired, wireless.
- Network summary: total, enabled, disabled.
- Device discovery.
- Client discovery.
- Network discovery.
- Port discovery with item prototypes for state, negotiated speed, maximum speed,
  and connector type.
- Empty port speed values are normalized to `0` Mbps, which avoids numeric item
  errors on disconnected or inactive ports.
- Legacy port telemetry discovery from `port_table`, with link state,
  negotiated speed, upload/download rate, RX/TX errors, RX/TX drops, PoE power,
  PoE voltage, PoE good state, PoE mode, and graph prototypes for traffic,
  errors/drops, and PoE.
- Legacy port telemetry uses one master item with dependent item prototypes, so
  large switch/AP environments do not call the UniFi API once per metric.
- Radio discovery with item prototypes for channel, channel width, frequency,
  and WLAN standard.
- System health from `/proxy/network/api/s/default/stat/device`: CPU, memory,
  load average, aggregate storage, uptime, and CPU temperature.
- Storage discovery from the legacy endpoint with per-volume used, free, total,
  utilization, trigger prototypes, and graph prototypes.
- WAN health from the legacy endpoint: latency, packet loss, availability,
  alive state, WAN IP, upload/download rate, and speedtest status, latency,
  last run, age, download, and upload results.
- WAN discovery for multi-WAN environments. The current test environment has
  one WAN, but the template includes WAN item prototypes for WAN2 and additional
  discovered WAN labels when the legacy payload exposes them.
- Radio performance from the legacy endpoint: channel utilization, self RX/TX
  utilization, retry percentage, connected stations, and satisfaction.
- Legacy radio performance uses one master item with dependent item prototypes,
  so AP-heavy environments do not call the UniFi API once per radio metric.
- Radio satisfaction values below zero are normalized to `0`, because some
  UniFi controllers return `-1` until that metric is available.
- A dashboard named `UniFi Controller Overview` with classic graphs for
  Internet activity, system health, and clients/devices.
- A dashboard named `Unifi Controller` with a modern SVG graph, version widget,
  and CPU/memory gauges.
- Triggers for offline devices, firmware updates, disabled networks, and
  application version changes, high CPU, high memory, high storage usage, and
  high CPU temperature, WAN latency, and WAN packet loss.

## External Script

The first external script is:

```text
unifi_udm_pro_api.py
```

It uses only Python standard library modules, so no extra `pip` dependencies are
required.

Install it on the Zabbix server or proxy external scripts directory:

```bash
sudo install -m 0755 unifi_udm_pro_api.py /usr/lib/zabbix/externalscripts/unifi_udm_pro_api.py
```

### Linux Test Environment

Set these variables before testing:

```bash
export UNIFI_API_URL="https://xxx.xxx.xxx.xxx"
export UNIFI_SITE_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export UNIFI_API_KEY="replace-with-your-api-key"
```

Do not store the real API key in Git-tracked files.

`UNIFI_SITE_ID` is recommended, but optional when the controller has only one
site. In that case, the script discovers the site automatically.

### Raw API Commands

```bash
./unifi_udm_pro_api.py info
./unifi_udm_pro_api.py sites
./unifi_udm_pro_api.py devices
./unifi_udm_pro_api.py clients
./unifi_udm_pro_api.py networks
./unifi_udm_pro_api.py device xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

From the Zabbix external scripts directory:

```bash
/usr/lib/zabbix/externalscripts/unifi_udm_pro_api.py info
/usr/lib/zabbix/externalscripts/unifi_udm_pro_api.py summary-devices
```

The script also accepts explicit positional arguments, which is useful for
Zabbix external checks:

```bash
./unifi_udm_pro_api.py info "{$UNIFI.API.URL}" "{$UNIFI.API.KEY}"
./unifi_udm_pro_api.py devices "{$UNIFI.API.URL}" "{$UNIFI.API.KEY}" "{$UNIFI.SITE.ID}"
```

### Summary Commands

```bash
./unifi_udm_pro_api.py summary-devices
./unifi_udm_pro_api.py summary-clients
./unifi_udm_pro_api.py summary-networks
./unifi_udm_pro_api.py system-health "$UNIFI_API_URL" "$UNIFI_API_KEY" default
./unifi_udm_pro_api.py wan-health "$UNIFI_API_URL" "$UNIFI_API_KEY" default
./unifi_udm_pro_api.py discover-wans "$UNIFI_API_URL" "$UNIFI_API_KEY" default
./unifi_udm_pro_api.py wan-field "$UNIFI_API_URL" "$UNIFI_API_KEY" default WAN latency_ms
```

`system-health` uses the legacy UniFi Network endpoint and returns CPU, memory,
load, aggregate storage, uptime, and temperature metrics for the UDM Pro.
`wan-health` uses the same endpoint and returns WAN latency, packet loss,
availability, upload/download rates, and speedtest data.
`discover-wans` returns low-level discovery rows for WAN interfaces. It is
prepared for labels such as `WAN`, `WAN2`, and additional WAN objects exposed by
UniFi.

### Low-Level Discovery Commands

```bash
./unifi_udm_pro_api.py discover-devices
./unifi_udm_pro_api.py discover-clients
./unifi_udm_pro_api.py discover-networks
./unifi_udm_pro_api.py discover-ports
./unifi_udm_pro_api.py discover-radios
./unifi_udm_pro_api.py legacy-discover-radios "$UNIFI_API_URL" "$UNIFI_API_KEY" default
```

The script automatically handles paginated endpoints such as `clients`.
When `discover-ports` or `discover-radios` is called without a device ID, it
discovers all devices first and then queries the detail endpoint only for
devices that expose `ports` or `radios`.

You can still test a single device manually:

```bash
./unifi_udm_pro_api.py discover-ports xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
./unifi_udm_pro_api.py discover-radios xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Suggested Next Additions

- Switch-level PoE budget from `total_used_power` and `total_max_power`.
- VPN tunnel discovery and status from the legacy `network_table`.
- DHCP lease count per VLAN from legacy network details.
- IDS/IPS signature status and rule count.
- WAN failover state and active WAN detection for multi-WAN environments.

### API Review Notes

The legacy `stat/device` payload contains several high-value fields that are
good candidates for future template expansion:

- Gateway identity and firmware: `model`, `version`, `displayable_version`,
  `kernel_version`, `architecture`, and `upgradable`.
- WAN health: `last_wan_status`, `last_wan_interfaces`, `wan1`, `wan2`,
  `uplink`, `uptime_stats`, and `speedtest-status`.
- Traffic and switch ports: `port_table`, `uplink`, `downlink_table`, and
  per-port counters under `stat.sw`.
- PoE and switch power: `poe_power`, `poe_voltage`, `poe_good`,
  `total_used_power`, `total_max_power`, and near-limit flags.
- Wireless quality: `radio_table_stats`, `vap_table`, retry percentage,
  channel utilization, station count, and satisfaction.
- Storage and temperature: `storage`, `temperatures`, and `overheating`.
- Security and IDS/IPS: `ids_ips_signature` rule count, update time, signature
  type, and activation state.
- Network services: `network_table`, VPN status, DHCP lease counts, IPv4 active
  leases, reported networks, and WAN failover state.

## Confirmed Local API Responses

The initial tests against the local UDM Pro Network API confirmed the following
site response:

```json
{
  "offset": 0,
  "limit": 25,
  "count": 1,
  "totalCount": 1,
  "data": [
    {
      "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "internalReference": "default",
      "name": "Default"
    }
  ]
}
```

Confirmed site values:

- Site ID: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Internal reference: `default`
- Site name: `Default`

The info endpoint confirmed the UniFi Network application version:

```json
{
  "applicationVersion": "10.3.58"
}
```

The device list endpoint confirmed these fields are available for low-level
discovery:

- `id`
- `macAddress`
- `ipAddress`
- `name`
- `model`
- `state`
- `supported`
- `firmwareVersion`
- `firmwareUpdatable`
- `features`
- `interfaces`

The client list endpoint confirmed paginated client discovery. The first page
returned 25 clients from a total of 28:

```json
{
  "offset": 0,
  "limit": 25,
  "count": 25,
  "totalCount": 28,
  "data": []
}
```

The collector must continue requesting pages while `offset + count` is lower
than `totalCount`.

Confirmed client discovery fields:

- `type`
- `id`
- `name`
- `connectedAt`
- `ipAddress`
- `macAddress`
- `uplinkDeviceId`
- `access.type`

The networks endpoint confirmed VLAN and zone discovery fields:

- `management`
- `id`
- `name`
- `enabled`
- `vlanId`
- `metadata.origin`
- `metadata.configurable`
- `zoneId`
- `default`

The tested site returned 6 gateway-managed networks.

The device detail endpoint for the UDM Pro confirmed port-level data:

- `interfaces.ports[].idx`
- `interfaces.ports[].state`
- `interfaces.ports[].connector`
- `interfaces.ports[].maxSpeedMbps`
- `interfaces.ports[].speedMbps`

The device detail endpoint for a FlexHD access point confirmed uplink and radio
data:

- `adoptedAt`
- `provisionedAt`
- `configurationId`
- `uplink.deviceId`
- `interfaces.radios[].wlanStandard`
- `interfaces.radios[].frequencyGHz`
- `interfaces.radios[].channelWidthMHz`
- `interfaces.radios[].channel`

Example port object:

```json
{
  "idx": 1,
  "state": "UP",
  "connector": "RJ45",
  "maxSpeedMbps": 1000,
  "speedMbps": 1000
}
```

Example radio object:

```json
{
  "wlanStandard": "802.11ac",
  "frequencyGHz": 5,
  "channelWidthMHz": 40,
  "channel": 136
}
```

Confirmed monitoring candidates from the official local API:

- Device count.
- Device state.
- Device support status.
- Device firmware version.
- Firmware update availability.
- Device IP address.
- Device provisioning timestamp.
- Device configuration ID.
- Physical port discovery.
- Physical port state.
- Physical port connector type.
- Physical port maximum speed.
- Physical port negotiated speed.
- UniFi Network application version.
- Access point uplink device.
- Access point radio discovery.
- Access point radio WLAN standard.
- Access point radio frequency band.
- Access point radio channel width.
- Access point radio channel.
- Client count.
- Wireless client count.
- Wired client count.
- Client discovery.
- Client IP address.
- Client uplink device.
- Client access type.
- Network count.
- Network enabled state.
- Network VLAN ID.
- Network management type.
- Network metadata origin.
- Network zone ID.
- Default network flag.

Confirmed Linux script tests from the Zabbix external scripts directory:

```bash
./unifi_udm_pro_api.py summary-devices
```

Returned:

```json
{"offline":0,"online":5,"total":5,"updatable":0}
```

```bash
./unifi_udm_pro_api.py discover-devices
```

Returned 5 discovered UniFi devices.

```bash
./unifi_udm_pro_api.py discover-ports xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Returned 11 discovered UDM Pro ports.

Confirmed trigger candidates:

- Device is not `ONLINE`.
- Device is not supported by the API.
- Firmware update is available.
- Device IP address changed.
- Firmware version changed.
- Physical port expected to be up is down.
- Physical port negotiated below maximum speed.
- Physical port speed changed.
- Access point uplink changed.
- Access point radio channel changed.
- Access point radio channel width changed.
- Important client disconnected or disappeared from discovery.
- Client IP address changed.
- Client uplink changed.
- Unexpected client access type.
- Network disabled unexpectedly.
- Network VLAN ID changed.
- Network zone changed.
- Default network changed.
