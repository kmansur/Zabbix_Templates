# Aligera Zabbix Templates

**English** | [Português (Brasil)](README.pt-BR.md)

Installation: **[English](INSTALL.md)** | [Português (Brasil)](INSTALL.pt-BR.md)

This directory contains Zabbix templates for monitoring Aligera telecom gateways.

## Aligera AG561 E1 by SNMP

The AG561 template was adapted and expanded for Zabbix 7.0 using the Aligera enterprise MIB (`1.3.6.1.4.1.41933`), SNMPv2-MIB and IF-MIB, and was validated against real Aligera AG561 devices.

Template file: [`7.0/template_aligera_ag561_e1_snmp.yaml`](7.0/template_aligera_ag561_e1_snmp.yaml)

### Tested environment

- Device: Aligera AG561
- Tested firmware: 8.16
- Zabbix: 7.0
- SNMP: v2c
- Template version: 3.0.0
- Vendor metadata: Net Tech
- Template group: `Templates/Network devices`

## Monitoring coverage

### Device and SNMP

- Product name
- System description and firmware
- System uptime
- SNMP availability
- ICMP availability
- ICMP packet loss
- ICMP latency
- SNMP system name, contact, location and object ID

### E1

- E1 interface count
- Current E1 alarm state
- Statistics uptime
- Code violations
- Slips
- CRC errors
- LOS events and accumulated LOS time
- AIS events and accumulated AIS time
- BFAE events and accumulated BFAE time
- MFAE events and accumulated MFAE time
- RAI events and accumulated RAI time
- Error/event rates
- Recent quality metrics
- Normalized events/hour
- Alarm duration percentages
- Operational healthy-time percentage
- Statistics reset detection

### Voice channels

Channel discovery uses the Aligera channel table and excludes `SIG(6)` entries from voice monitoring.

On the validated AG561 configuration:

- Channel table entries: 31
- Voice channels: 30
- Signaling entry: TS16 / `SIG(6)`

The template monitors channel type/state, free/busy/blocked/N/A channels, utilization and 24-hour peak occupancy/utilization.

### SIP

SIP peer discovery includes peer name, host/IP, port, Keepalive and Registry. Keepalive and Registry are strings in the Aligera MIB, so the template records informational changes without assuming that `Unmonitored` or `-` indicate failure.

### Ethernet / IF-MIB

Ethernet interfaces are discovered using `ifType=6` (`ethernetCsmacd`). The template monitors administrative/operational state, MTU, MAC, 64-bit RX/TX traffic, errors, discards and error/discard growth rates. Administratively disabled interfaces do not generate link-down problems.

## User macros

All configurable user macros exported by template version 3.0.0 are listed below. Values may be overridden at host level when a specific AG561 has a different capacity or operational baseline.

| Macro | Default | Purpose |
|---|---:|---|
| `{$AG561.CHANNEL.NA.WARN}` | `1` | Minimum number of voice channels in N/A state that generates a Warning when persistent for 5 minutes. |
| `{$AG561.CHANNEL.UTIL.HIGH}` | `90` | Average channel-utilization percentage over 5 minutes for a High alert. |
| `{$AG561.CHANNEL.UTIL.WARN}` | `80` | Average channel-utilization percentage over 5 minutes for a Warning alert. |
| `{$AG561.E1.EXPECTED}` | `1` | Expected number of E1 interfaces. Can be overridden on the host. |
| `{$AG561.SIG.EXPECTED}` | `1` | Expected number of SIG entries. Can be overridden on the host. |
| `{$AG561.SIP.EXPECTED}` | `1` | Expected number of SIP peers. Can be overridden on the host. |
| `{$AG561.VOICE.EXPECTED}` | `30` | Expected number of voice channels. Can be overridden on the host. |
| `{$E1.CODE.RATE.WARN}` | `0` | Code Violations/s rate above this value generates an alert. Zero means alert on any increase. |
| `{$E1.CRC.RATE.WARN}` | `0` | CRC errors/s rate above this value generates an alert. Zero means alert on any increase. |
| `{$E1.SLIP.RATE.HIGH}` | `0.1` | Persistent Slips/s rate for a High alert after 15 minutes. Tune after observing the real baseline. |
| `{$E1.SLIP.RATE.WARN}` | `0` | Slips/s rate above this value generates an alert. Zero means alert on any increase. |
| `{$ICMP.LOSS.WARN}` | `20` | Average ICMP packet loss (%) that generates a Warning alert. |
| `{$ICMP.RESPONSE.WARN}` | `100` | Average ICMP latency in milliseconds that generates a Warning alert. |
| `{$IF.DISCARD.RATE.WARN}` | `0` | RX/TX discard rate per second above this value generates a Warning. Zero alerts on any persistent increase. |
| `{$IF.ERROR.RATE.WARN}` | `0` | RX/TX error rate per second above this value generates a Warning. Zero alerts on any persistent increase. |

### Macro tuning notes

- The four `*.EXPECTED` macros should describe the real hardware/service configuration. The validated AG561 uses 1 E1, 30 voice channels, 1 SIG entry and 1 SIP peer.
- Rate macros with default `0` intentionally alert on any new growth. Raise them only after observing a known-good baseline.
- `{$E1.SLIP.RATE.HIGH}` is intentionally separate from the Warning threshold and should be tuned after collecting production history.
- ICMP and channel-utilization thresholds are operational defaults and may be overridden per host.

## Triggers

The template includes triggers for ICMP/SNMP availability, packet loss, latency, voice-channel BLOCKED/N/A, channel utilization, E1 LOS/AIS/BFAE/MFAE/RAI, CRC/slips/code-violation growth, persistent slips, E1 statistics reset, reboot, Ethernet link state and errors/discards, capacity mismatch, and informational SIP/firmware changes.

## Dashboards

The template includes:

- Operational view
- Diagnostics
- Capacity
- SIP

The operational Honeycomb displays only the 30 voice channels and excludes the signaling timeslot.

## SNMP traps

Version 3.x supports:

- `e1AlarmsChange` — `1.3.6.1.4.1.41933.1.2.3.1`
- `chanStatusChange` — `1.3.6.1.4.1.41933.1.3.3.1`
- `sipKeepaliveChange` — `1.3.6.1.4.1.41933.1.4.3.1`
- `snmptrap.fallback` for unmatched traps

Trap events are informational and supplemental; polling-based triggers remain authoritative for persistent fault state.

For complete installation and trap-receiver configuration, see **[INSTALL.md](INSTALL.md)**.

## Important notes

- Raw E1 counters are cumulative since the last E1 statistics reset. A historical non-zero value does not by itself indicate an active fault.
- Rate-based and recent-quality items detect active degradation.
- E1 alarm-duration and healthy-time percentages are operational indicators, not contractual SLA measurements.
- The device may return `chanNumber=31`; validated devices contain 30 MFCR2 voice channels plus one signaling entry (`SIG`) at TS16.
- `ifSpeed` / `ifHighSpeed` are not used because the tested AG561 firmware returned unreliable values for physical Ethernet interfaces.
- SNMPv2c does not provide encryption. Use it only on trusted/private networks and restrict UDP/161 and UDP/162 with firewall rules.

## Credits

The initial work was based on the AG562 Zabbix template by Douglas Boldrini:

- Original repository: https://github.com/boldrinidouglas/ZBX-GRA-ALIGERA
- Original template: `TEMPLATE_TELEFONIA_AG562_E1_LLD_SNMP_ZBX-5.0.xml`

The AG561 adaptation, Zabbix 7.0 modernization, expanded MIB coverage, dashboards, triggers, capacity metrics, IF-MIB monitoring and SNMP trap support were developed and validated for the Net Tech environment.
