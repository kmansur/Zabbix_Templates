# Validation Checklist

Use this checklist before promoting the template to production. Version 0.7.0
adds parallel validation of the documented UniFi Network Integration API device
statistics endpoint while keeping legacy telemetry in place.

## 1. Script Sanity

```bash
python3 -m py_compile unifi_udm_pro_api.py
```

## 2. Integration API Reachability

```bash
python3 unifi_udm_pro_api.py info "$UNIFI_API_URL" "$UNIFI_API_KEY"
python3 unifi_udm_pro_api.py sites "$UNIFI_API_URL" "$UNIFI_API_KEY"
```

Expected: valid JSON payloads without an `error` field.

## 3. Official Device Statistics

First identify the site ID and gateway device ID, then test:

```bash
python3 unifi_udm_pro_api.py devices "$UNIFI_API_URL" "$UNIFI_API_KEY" "$UNIFI_SITE_ID"
python3 unifi_udm_pro_api.py device-stats "$UNIFI_API_URL" "$UNIFI_API_KEY" "$UNIFI_SITE_ID" "$UNIFI_GATEWAY_DEVICE_ID"
```

Expected fields on Network versions supporting the documented endpoint include
`uptimeSec`, `cpuUtilizationPct`, `memoryUtilizationPct`, load averages, and
`uplink.rxRateBps` / `uplink.txRateBps`.

## 4. TLS Validation

The templates define `{$UNIFI.TLS.ARG}`.

- Default `--timeout=20`: preserves existing behavior, including self-signed
  console certificates.
- Set to `--verify-tls`: the collector validates the HTTPS certificate using the
  Zabbix server/proxy system trust store.

After enabling verification, confirm both Integration API and legacy collector
health items remain available.

## 5. Legacy Network API Payloads

```bash
python3 unifi_udm_pro_api.py system-health "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py gateway-info "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py wan-health "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py network-services "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py poe-budget "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py radio-performance "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py port-telemetry "$UNIFI_API_URL" "$UNIFI_API_KEY" default
```

Expected: valid JSON payloads; numeric fields should be numeric.

## 6. Zabbix Template Checks

1. Import `7.0/UniFi_UDM_Pro_API_Monitoring_7.0.yaml` for Zabbix 7.0 or
   `8.0/UniFi_UDM_Pro_API_Monitoring_8.0.yaml` for Zabbix 8.0.
2. Link the template to a test UDM Pro host.
3. Set `{$UNIFI.API.URL}`, `{$UNIFI.API.KEY}`, `{$UNIFI.SITE.ID}` when needed,
   and `{$UNIFI.NETWORK.SITE}`.
4. Confirm the official gateway statistics discovery selects the expected device.
5. Confirm official CPU, memory, load, uptime, and uplink items receive data.
6. Confirm legacy collector status items remain `1` and existing dashboards keep data.
7. Confirm no dependent item is unsupported after the first collection cycles.

## 7. Trigger Validation

1. Confirm the official statistics collection trigger stays recovered.
2. Confirm informational firmware/reboot triggers stay stable.
3. Confirm WAN/radio/PoE threshold triggers recover after values normalize.
4. Confirm `gateway-info` dependent items (`name`, `type`, `mac`, `model`, `version`) are populated.
