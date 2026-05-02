# Changelog

All notable changes to this project are documented here.

## 0.5.0 - Unreleased

### Added

- Added legacy port telemetry discovery from `port_table` with item prototypes
  for link state, negotiated speed, traffic rates, RX/TX errors, RX/TX drops,
  PoE power, PoE voltage, PoE good state, and PoE mode.
- Added graph prototypes for legacy port traffic, errors/drops, and PoE.
- Added `legacy-discover-ports` and `legacy-port-field` script commands.

### Changed

- Updated script version to `0.5.0`.
- Updated template vendor version to `0.5-0`.

## 0.4.4 - Previous Unreleased

### Fixed

- Normalized empty port speed and max speed values to `0` so Zabbix numeric
  unsigned items do not reject inactive-port API placeholders.

### Changed

- Updated script version to `0.4.4`.
- Updated template vendor version to `0.4-4`.

## 0.4.3 - Previous Unreleased

### Fixed

- Normalized negative legacy radio satisfaction values to `0` so Zabbix numeric
  unsigned items do not reject UniFi `-1` placeholders.

### Changed

- Updated script version to `0.4.3`.
- Updated template vendor version to `0.4-3`.

## 0.4.2 - Previous Unreleased

### Fixed

- Removed the WAN IP address change trigger because the target Zabbix import
  rejected the `diff()` trigger function.

### Changed

- Updated script version to `0.4.2`.
- Updated template vendor version to `0.4-2`.

## 0.4.1 - Previous Unreleased

### Fixed

- Fixed the `Unifi Controller` dashboard page export structure by adding a
  named page before the `widgets` list.

### Changed

- Updated script version to `0.4.1`.
- Updated template vendor version to `0.4-1`.

## 0.4.0 - Previous Unreleased

### Added

- Added fixed WAN items for alive state, IP address, speedtest latency,
  speedtest last run, speedtest age, and speedtest status.
- Added fixed system uptime item from the existing system health master item.
- Added an informational trigger for stale WAN speedtest results.
- Added an informational trigger for WAN IP address changes.
- Added the `Unifi Controller` dashboard with a modern SVG graph, version item
  widget, and CPU/memory gauges.
- Added API review notes to the README with candidate telemetry fields for the
  next template iterations.

### Changed

- Removed the previous experimental dashboard.
- Updated script version to `0.4.0`.
- Updated template vendor version to `0.4-0`.

## 0.3.3 - Previous Unreleased

### Added

- Added storage volume low-level discovery to the template.
- Added per-storage used, free, total, and utilization item prototypes.
- Added per-storage utilization trigger prototypes and usage graph prototypes.

### Fixed

- Allowed `storage-field` to auto-select the UDM device, matching
  `discover-storage` and the WAN helper behavior.
- Moved the WAN alive trigger prototype to the discovery rule level for cleaner
  Zabbix import compatibility.

### Changed

- Updated script version to `0.3.3`.
- Updated template vendor version to `0.3-3`.

## 0.3.2 - Previous Unreleased

### Fixed

- Masked remaining real environment identifiers in the README examples and
  confirmed API response notes.
- Replaced the template default API URL with a placeholder value.
- Replaced the script docstring example URL with a generic placeholder.

### Changed

- Updated script version to `0.3.2`.
- Updated template vendor version to `0.3-2`.

## 0.3.1 - Previous Unreleased

### Fixed

- Fixed WAN discovery item prototypes returning `{"error":"missing WAN field arguments"}`
  when `{$UNIFI.DEVICE.ID}` is empty.
- Simplified WAN prototype keys so `wan-field` uses the auto-detected UDM device
  by default: URL, API key, legacy site, WAN name, and field.
- Kept backward compatibility in the script for older `wan-field` keys that
  still pass an explicit device ID before the WAN name.

### Changed

- Updated script version to `0.3.1`.
- Updated template vendor version to `0.3-1`.

## 0.3.0 - Previous Unreleased

### Added

- Added explicit project versioning across the external script and Zabbix
  template vendor metadata.
- Added clearer script documentation and docstrings for API surfaces, error
  handling, discovery helpers, scalar item helpers, system health, WAN health,
  and radio telemetry.
- Added multi-WAN discovery with the `discover-wans` command.
- Added `wan-field` scalar collection for WAN item prototypes.
- Added WAN low-level discovery to the Zabbix template:
  - WAN latency.
  - WAN packet loss.
  - WAN availability.
  - WAN download rate.
  - WAN upload rate.
  - WAN alive state.
  - Per-WAN Internet activity graph prototype.
- Added `UniFi Controller Overview - Experimental`, a second dashboard focused
  on a UniFi-like layout with Internet, Wireless, and System pages.
- Added `UniFi WAN quality` graph for latency, packet loss, and availability.

### Changed

- Kept the original single-WAN items for simple UDM Pro deployments, while
  adding WAN discovery for future multi-WAN deployments.
- Updated script version to `0.3.0`.
- Updated template vendor version to `0.3-0`.

### Notes

- Multi-WAN support is implemented from the legacy payload structure
  (`uptime_stats`, `last_wan_interfaces`, `wan1`, `wan2`, and `uplink`), but the
  current test environment has only one WAN. A real multi-WAN import should be
  validated when a WAN2 device is available.

## 0.2.0 - Previous Unreleased

### Added

- Added legacy UniFi Network API support through
  `/proxy/network/api/s/<site>/stat/device`.
- Added UDM Pro system health collection:
  - CPU utilization.
  - Memory utilization.
  - Load average.
  - Aggregate storage usage.
  - CPU temperature.
- Added WAN health collection:
  - WAN latency.
  - Packet loss derived from WAN availability.
  - WAN upload and download rates.
  - Speedtest download, upload, and latency.
- Added `UniFi Controller Overview` dashboard with Internet activity, system
  health, and clients/devices graphs.
- Added graph definitions for Internet activity, system health, and clients.
- Added legacy radio performance discovery from `radio_table_stats`.
- Added radio performance item prototypes:
  - Channel utilization (`cu_total`).
  - Self RX utilization.
  - Self TX utilization.
  - TX retry percentage.
  - Connected stations.
  - Satisfaction.
- Added radio graph prototypes for channel utilization and radio quality.

### Changed

- Expanded the Zabbix template with system health, storage, WAN health, and
  dashboard macros.
- Extended the external script with `legacy-discover-radios` and
  `legacy-radio-field`.

## 0.1.0 - Initial Development

### Added

- Created the `UniFi UDM Pro API Monitoring` project directory.
- Added project README with API key creation and security guidance.
- Added `unifi_udm_pro_api.py` external script.
- Added support for the local UniFi Network Integration API:
  - `info`
  - `sites`
  - `devices`
  - `clients`
  - `networks`
  - `device`
  - `client`
- Added automatic pagination support.
- Added Zabbix low-level discovery commands:
  - Devices.
  - Clients.
  - Networks.
  - Ports.
  - Radios.
- Added summary commands for devices, clients, and networks.
- Added an importable Zabbix 7.0 template.
- Added device, client, network, port, and radio discovery to the template.
- Added triggers for offline devices, firmware updates, disabled networks, and
  application version changes.

### Fixed

- Removed unsupported tags from discovery rules for Zabbix 7.0 import
  compatibility.
- Replaced deterministic UUIDv5 values with UUIDv4 values accepted by Zabbix.
- Normalized boolean low-level discovery macro values to lowercase `true` and
  `false`.
