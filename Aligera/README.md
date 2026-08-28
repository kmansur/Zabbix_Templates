# Aligera Zabbix Templates

This directory contains Zabbix templates for monitoring Aligera telecom gateways.

## Aligera AG561 E1 by SNMP

The AG561 template was adapted and expanded for Zabbix 7.0 using the Aligera enterprise MIB (`1.3.6.1.4.1.41933`), SNMPv2-MIB and IF-MIB, and was validated against real Aligera AG561 devices.

### Tested environment

- Device: Aligera AG561
- Tested firmware: 8.16
- Zabbix: 7.0
- SNMP: v2c
- Vendor metadata: Net Tech
- Template group: `Templates/Network devices`

## Monitoring coverage

The template includes monitoring for:

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

The template monitors:

- Channel type
- Channel state: BLOCKED, IDLE, BUSY, N/A
- Free channels
- Busy channels
- Blocked channels
- N/A channels
- Channel utilization percentage
- Peak busy channels over 24 hours
- Peak utilization over 24 hours

### SIP

SIP peer discovery includes:

- Peer name
- Host/IP
- Port
- Keepalive state
- Registry state

The Aligera MIB exposes Keepalive and Registry as strings rather than enumerated states. For this reason, the template records informational events when these values change but does not assume that values such as `Unmonitored` or `-` indicate a failure.

### Ethernet / IF-MIB

Ethernet interfaces are discovered using `ifType=6` (`ethernetCsmacd`).

The template monitors:

- Administrative status
- Operational status
- MTU
- MAC address
- 64-bit RX traffic via `ifHCInOctets`
- 64-bit TX traffic via `ifHCOutOctets`
- RX errors
- TX errors
- RX discards
- TX discards
- Error/discard growth rates

Interfaces that are administratively down do not generate link-down problems.

## Triggers

The template includes triggers for, among others:

- ICMP unavailability
- SNMP unavailability
- Packet loss
- High ICMP latency
- Voice channel BLOCKED
- Voice channel N/A
- High channel utilization
- E1 LOS
- E1 AIS
- E1 BFAE
- E1 MFAE
- E1 RAI
- Increasing CRC errors
- Increasing slips
- Persistent slips
- Increasing code violations
- E1 statistics reset
- Device reboot
- Ethernet interface operationally down while administratively up
- Ethernet errors/discards increasing
- Configuration/capacity mismatch
- Informational SIP configuration/state changes
- Informational firmware/system-description changes

Thresholds are exposed through Zabbix user macros where appropriate.

## Dashboards

The template includes template dashboards for:

- Operational view
- Diagnostics
- Capacity
- SIP

The operational channel Honeycomb displays only the 30 voice channels and excludes the signaling timeslot.

## SNMP traps

Version 3.x adds support for the Aligera notifications defined by the MIB:

- `e1AlarmsChange`
- `chanStatusChange`
- `sipKeepaliveChange`

The template also includes an unmatched SNMP trap fallback item for diagnostics.

### Zabbix trap receiver requirements

Importing the template does not configure the operating system SNMP trap receiver automatically. The Zabbix Server or Proxy receiving traps must have SNMP trap processing enabled, for example:

```ini
StartSNMPTrapper=1
SNMPTrapperFile=/var/log/snmptrap/snmptrap.log
```

`snmptrapd` or another compatible trap handler must write incoming traps in the format expected by Zabbix. The AG561 must also be configured to send traps to the IP address of the Zabbix Server or Proxy responsible for the monitored host.

## Important notes

- Raw E1 counters are cumulative since the last E1 statistics reset. A non-zero historical value does not by itself indicate an active fault.
- Rate-based and recent-quality items are used to detect active degradation.
- E1 alarm-duration and healthy-time percentages are operational indicators, not contractual SLA measurements.
- The device may return `chanNumber=31`; validated devices contain 30 MFCR2 voice channels plus one signaling entry (`SIG`) at TS16.
- `ifSpeed` / `ifHighSpeed` were not used because the tested AG561 firmware returned unreliable values for physical Ethernet interfaces.

## Credits

The initial work was based on the AG562 Zabbix template by Douglas Boldrini:

- Original repository: https://github.com/boldrinidouglas/ZBX-GRA-ALIGERA
- Original template: `TEMPLATE_TELEFONIA_AG562_E1_LLD_SNMP_ZBX-5.0.xml`

The AG561 adaptation, Zabbix 7.0 modernization, expanded MIB coverage, dashboards, triggers, capacity metrics, IF-MIB monitoring and SNMP trap support were developed and validated for the Net Tech environment.
