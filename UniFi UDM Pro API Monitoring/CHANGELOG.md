# Changelog

## 0.8.0 - 2026-09-04

- Unified the UniFi monitoring stack into **one template per Zabbix major version** and **one external collector**: `unifi_udm_pro_api.py`.
- Removed the temporary dashboard companion template and `unifi_dashboard_telemetry.py` deployment model.
- Added rolling client and DPI traffic windows for `1h`, `1d`, `1w` and `1m` (30 days).
- Added current wireless client RSSI and Wi-Fi association/authentication/DHCP/DNS telemetry.
- Added DPI catalog name resolution using UniFi compound IDs `(category << 16) + application`.
- Optimized dashboard traffic collection so one v2 `/traffic` request supplies both client and application rankings for each window.
- Validated the v2 traffic endpoint with Unix epoch milliseconds on UniFi Network 10.6.101.
- Live-tested 1-week and 30-day traffic queries at approximately 0.74 s and 1.00 s respectively.
- Removed temporary one-argument ranking compatibility keys; Dashboard 0.2 uses only period-aware contracts.
- Simplified repository layout and installation documentation.

## 0.7.0 - 2026-09-04

- Added UniFi Network 10.6 support using the documented Integration API `statistics/latest` endpoint alongside existing operational telemetry.
- Added CPU, memory, load average, uptime and uplink RX/TX statistics.
- Added collector health/error items for official statistics collection.
- Added optional TLS certificate verification through `{$UNIFI.TLS.ARG}`.
- Updated API-key documentation for **UniFi Network > Integrations**.

Earlier development history remains available in the Git repository and merged pull requests.
