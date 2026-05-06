# Validation Checklist

Use this checklist before promoting the template to production.

## 1. Script Sanity

```bash
python3 -m py_compile unifi_udm_pro_api.py
```

## 2. API Reachability

```bash
python3 unifi_udm_pro_api.py info "$UNIFI_API_URL" "$UNIFI_API_KEY"
python3 unifi_udm_pro_api.py sites "$UNIFI_API_URL" "$UNIFI_API_KEY"
```

Expected: valid JSON payloads without an `error` field.

## 3. Network API Payloads

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

## 4. Zabbix Template Checks

1. Import `7.0/UniFi_UDM_Pro_API_Monitoring_7.0.yaml` for Zabbix 7.0
   or `8.0/UniFi_UDM_Pro_API_Monitoring_8.0.yaml` for Zabbix 8.0.
2. Link template to a test UDM Pro host.
3. Set macros:
   - `{$UNIFI.API.URL}`
   - `{$UNIFI.API.KEY}` (secret)
   - `{$UNIFI.NETWORK.SITE}`
4. Confirm collector status items are `1`.
5. Confirm no dependent item is unsupported after the first data collection cycle.

## 5. Trigger Validation

1. Confirm informational firmware/reboot triggers stay stable.
2. Confirm WAN/radio/PoE threshold triggers recover after values normalize.
3. Confirm `gateway-info` dependent items (`name`, `type`, `mac`, `model`, `version`) are populated.
