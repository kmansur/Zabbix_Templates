# Changelog

Portuguese version: [CHANGELOG.pt-BR.md](CHANGELOG.pt-BR.md)

All notable changes to this project are documented here.

Documentation maintenance: when this English changelog is updated, update
`CHANGELOG.pt-BR.md` in the same change.

## 0.6.10 - Unreleased

### Added

- Added gateway identity dependent items from `gateway-info` for:
  - Gateway name
  - Gateway type
  - Gateway MAC address
- Added informational trigger for recent gateway reboot using
  `unifi.system.uptime` and `{$UNIFI.UPTIME.REBOOT.WINDOW}`.
- Added `docs/VALIDATION.md` with script, API, and template checks.

### Changed

- Updated template vendor version to `0.6-10`.
- Updated README and README.pt-BR to the current project version and layout
  standard used in recent template projects.

## 0.6.6 - Unreleased

### Added

- Added `gateway-info` collection from the Network API device payload for
  gateway identity and firmware metadata.
- Added gateway model, firmware version, displayable version, kernel version,
  architecture, and firmware upgrade availability items.
- Added gateway info collector health items.
- Added informational triggers for gateway firmware update availability and
  firmware version changes.

### Changed

- Updated script version to `0.6.6`.
- Updated template vendor version to `0.6-6`.

## 0.6.5 - Unreleased

### Added

- Added device-level PoE budget collection from Network API power fields and
  PoE-capable port data.
- Added PoE budget low-level discovery with used, maximum, available,
  utilization, PoE-capable port count, and near-limit item prototypes.
- Added warning trigger prototypes for high PoE budget utilization and explicit
  PoE near-limit flags.
- Added PoE budget graph prototypes and collector health items.
- Added `{$UNIFI.POE.BUDGET.WARN}` for PoE budget utilization tuning.

### Changed

- Updated script version to `0.6.5`.
- Updated template vendor version to `0.6-5`.

## 0.6.4 - Unreleased

### Added

- Added `network-services` collection from the Network API device payload for
  DHCP, VPN, and IDS/IPS telemetry.
- Added DHCP enabled network and active lease counters.
- Added VPN total, enabled, and up tunnel counters, with a warning trigger when
  enabled VPN tunnels are not up.
- Added IDS/IPS enabled state, mode, signature rule count, signature version,
  last update, and signature age, with a stale signature warning trigger.
- Added collector health items for the network services master item.
- Added `{$UNIFI.IDS.SIGNATURE.MAX_AGE}` for IDS/IPS signature age tuning.

### Changed

- Updated script version to `0.6.4`.
- Updated template vendor version to `0.6-4`.

## 0.6.3 - Unreleased

### Added

- Added WAN failover visibility for multi-WAN deployments: active WAN, WAN
  count, failover enabled state, primary-WAN-active state, and failover state.
- Added per-WAN discovery metadata for role, active state, and failover state.
- Added a warning trigger when multi-WAN/failover is available but the primary
  WAN is no longer the active uplink.
- Controller-level fixed WAN items now follow the active uplink when no WAN
  label is passed, while per-WAN prototypes keep explicit labels.

### Changed

- Updated script version to `0.6.3`.
- Updated template vendor version to `0.6-3`.

## 0.6.2 - Unreleased

### Changed

- Removed `legacy` from visible template item names, trigger names, graph names,
  and item keys. The template now uses Network API wording for those metrics.
- Renamed the Network API site macro from `{$UNIFI.LEGACY.SITE}` to
  `{$UNIFI.NETWORK.SITE}`.
- Added script command aliases such as `port-telemetry`,
  `discover-port-telemetry`, `radio-performance`, and
  `discover-radio-performance` while keeping the previous command names for
  manual compatibility.
- Updated template vendor version to `0.6-2`.

## 0.6.1 - Unreleased

### Fixed

- Increased the `UniFi Clients` dashboard widget legend from two lines to three
  lines so all three client series are visible in the `Unifi Controller`
  dashboard.

### Changed

- Updated template vendor version to `0.6-1`.

## 0.6.0 - Unreleased

### Added

- Added collector health dependent items and triggers for Integration API,
  legacy system, legacy WAN, legacy port, and legacy radio master items.
- Added last-error text items for the same collector surfaces to make no-data
  troubleshooting faster.
- Added low-level discovery include filter macros for devices, networks,
  clients, ports, radios, storage, and WAN labels.
- Added warning triggers for low WAN availability, high radio utilization, high
  radio retry percentage, and low radio satisfaction.

### Changed

- Updated script version to `0.6.0`.
- Updated template vendor version to `0.6-0`.
- Replaced the `Unifi Controller` dashboard with a split WAN traffic, WAN
  quality, clients, and system gauge layout.

### Fixed

- Fixed legacy API URL construction when `{$UNIFI.API.URL}` is configured with
  the full `/proxy/network/integration/v1` path instead of only the UDM Pro root
  URL.
- Fixed boolean normalization for legacy port, PoE, and WAN status fields so
  string values such as `false`, `0`, and `down` are not treated as active.

## 0.5.3 - Previous Unreleased

### Fixed

- Removed `{$UNIFI.DEVICE.ID}` from fixed system and WAN master item keys so
  controller-level graphs keep working even when a host has a mismatched device
  ID macro. The script still supports explicit device IDs for manual legacy
  endpoint tests.
- Treat unresolved Zabbix user macros such as `{$UNIFI.DEVICE.ID}` as empty
  optional arguments in the script.
- Fall back to the `default` legacy site when an optional legacy site argument
  is empty or unresolved.

### Changed

- Updated script version to `0.5.3`.
- Updated template vendor version to `0.5-3`.

## 0.5.2 - Previous Unreleased

### Added

- Added a `legacy-radios` master command that returns normalized legacy radio
  performance telemetry as a compact device/radio map.

### Changed

- Converted legacy radio performance item prototypes from external checks to
  dependent item prototypes backed by the `legacy-radios` master item.
- Kept `legacy-radio-field` available for manual testing and compatibility.
- Updated script version to `0.5.2`.
- Updated template vendor version to `0.5-2`.

## 0.5.1 - Previous Unreleased

### Added

- Added a `legacy-ports` master command that returns normalized legacy port
  telemetry as a compact device/port map.

### Changed

- Converted legacy port telemetry item prototypes from external checks to
  dependent item prototypes backed by the `legacy-ports` master item.
- Kept `legacy-port-field` available for manual testing and compatibility.
- Updated script version to `0.5.1`.
- Updated template vendor version to `0.5-1`.

## 0.5.0 - Previous Unreleased

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
