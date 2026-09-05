# UniFi UDM Pro API Monitoring 0.8 validation

Validated reference environment:

- UniFi Network 10.6.101
- UniFi OS 5.1.31
- Zabbix 8.0.0beta2
- local Network API key from **UniFi Network > Integrations**

## Collector validation completed

```bash
./unifi_udm_pro_api.py version
./unifi_udm_pro_api.py info "$UDM" "$KEY" --timeout=20
./unifi_udm_pro_api.py dashboard-client-status "$UDM" "$KEY" "$SITE" --timeout=20
./unifi_udm_pro_api.py wifi-connectivity "$UDM" "$KEY" "$SITE" --timeout=20
./unifi_udm_pro_api.py dpi-catalog "$UDM" "$KEY" "$SITE" --timeout=20
```

The following rolling traffic windows were live-tested with `dashboard-traffic`:

```text
3600       1 hour
86400      1 day
604800     1 week
2592000    30 days
```

Observed response times for the larger windows were approximately 0.74 s for one week and 1.00 s for 30 days.

Validated data:

- current client identity and RSSI;
- per-client traffic rankings;
- site DPI traffic rankings;
- 2,112-entry DPI application catalog;
- compound DPI application IDs `(category << 16) + application`;
- Wi-Fi association, authentication, DHCP and DNS success ratios;
- v2 traffic timestamps in Unix epoch milliseconds.

## Template validation

The final repository contains one template per Zabbix major version:

```text
7.0/UniFi_UDM_Pro_API_Monitoring_7.0.yaml
8.0/UniFi_UDM_Pro_API_Monitoring_8.0.yaml
```

The templates were parsed successfully during the 0.8 consolidation build and contain the period-aware client and DPI contracts for `1h`, `1d`, `1w` and `1m`.

Before tagging a later release, validate at minimum:

1. Python syntax with `python3 -m py_compile unifi_udm_pro_api.py`.
2. YAML parsing for both templates.
3. `version` and `info` collector commands.
4. One short and one long `dashboard-traffic` window.
5. Zabbix master items and dependent discovery rules.
6. Dashboard period switching and ranking changes.
