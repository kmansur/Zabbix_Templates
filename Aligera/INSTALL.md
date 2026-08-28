# Installation and Configuration — Aligera AG561 E1 by SNMP

**English** | [Português (Brasil)](INSTALL.pt-BR.md)

Back to: [README.md](README.md)

This guide covers installation and configuration of the `Aligera AG561 E1 by SNMP` template for Zabbix 7.0, including SNMP polling and SNMP trap reception.

Template file: [`7.0/template_aligera_ag561_e1_snmp.yaml`](7.0/template_aligera_ag561_e1_snmp.yaml)

## 1. Validated environment

- Device: Aligera AG561
- Tested firmware: 8.16
- Zabbix: 7.0
- SNMP polling: SNMPv2c
- Template version: 3.0.0
- Vendor metadata: Net Tech
- Template group: `Templates/Network devices`
- Aligera enterprise OID: `1.3.6.1.4.1.41933`

The template also uses SNMPv2-MIB and IF-MIB objects.

## 2. Network requirements

Allow the following traffic only between the monitoring system and the AG561 devices:

| Direction | Protocol/port | Purpose |
|---|---|---|
| Zabbix Server/Proxy → AG561 | UDP/161 | SNMP polling |
| AG561 → Zabbix Server/Proxy | UDP/162 | SNMP traps |
| Zabbix Server/Proxy → AG561 | ICMP | Availability, packet loss and latency |

For SNMPv2c, use a dedicated community and keep this traffic on a trusted/private network. SNMPv2c does not provide encryption or strong sender authentication.

## 3. Install SNMP tools on the Zabbix Server or Proxy

Debian/Ubuntu example:

```bash
apt update
apt install -y snmp snmptrapd curl
```

The `snmp` package provides `snmpget`, `snmpwalk` and `snmptrap` utilities. `snmptrapd` is required only on the system that will receive traps.

## 4. Verify SNMP polling before importing the template

Replace `COMMUNITY` and `AG561_IP`.

Check system description:

```bash
snmpget -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.2.1.1.1.0
```

Expected on the validated firmware:

```text
Aligera AG561 8.16
```

Check the Aligera enterprise branch:

```bash
snmpwalk -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.4.1.41933
```

Useful capacity checks:

```bash
snmpget -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.4.1.41933.1.2.1.0
snmpget -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.4.1.41933.1.3.1.0
snmpget -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.4.1.41933.1.4.1.0
```

On the validated configuration these return:

```text
E1 interfaces: 1
Channel table entries: 31
SIP peers: 1
```

The 31 channel-table entries are 30 MFCR2 voice channels plus the TS16 signaling entry (`SIG`). The template automatically excludes the `SIG(6)` entry from voice-channel monitoring.

## 5. Import the Zabbix template

In Zabbix 7.0:

1. Open **Data collection → Templates**.
2. Click **Import**.
3. Select `Aligera/7.0/template_aligera_ag561_e1_snmp.yaml`.
4. Review the import options.
5. Import the template.

The template should appear as:

```text
Aligera AG561 E1 by SNMP
```

Template group:

```text
Templates/Network devices
```

## 6. Create or configure the AG561 host

In **Data collection → Hosts**:

1. Create the host or open an existing AG561 host.
2. Add an **SNMP interface**.
3. Set the device IP address.
4. Set port `161`.
5. Select **SNMPv2**.
6. Configure the same community used by the device.
7. Link the template **Aligera AG561 E1 by SNMP**.
8. Save the host.

### Important requirement for traps

The IP or DNS selected on the Zabbix SNMP interface must match the source address seen in the received trap. Zabbix associates SNMP traps with hosts by comparing the received trap address with the host SNMP interface.

If the AG561 sends traps from a different source IP than the address configured on the host SNMP interface, trap items will not be matched correctly.

## 7. User macros

The template exports 15 macros. Override them at host level only when the real configuration or baseline requires it.

| Macro | Default | Recommendation |
|---|---:|---|
| `{$AG561.CHANNEL.NA.WARN}` | `1` | Keep `1` unless N/A is intentionally used on voice channels. TS16/SIG is already excluded. |
| `{$AG561.CHANNEL.UTIL.HIGH}` | `90` | High channel-utilization threshold over 5 minutes. |
| `{$AG561.CHANNEL.UTIL.WARN}` | `80` | Warning channel-utilization threshold over 5 minutes. |
| `{$AG561.E1.EXPECTED}` | `1` | Set to the real number of E1 interfaces. |
| `{$AG561.SIG.EXPECTED}` | `1` | Validated configuration has one signaling entry. |
| `{$AG561.SIP.EXPECTED}` | `1` | Set to the real number of SIP peers. |
| `{$AG561.VOICE.EXPECTED}` | `30` | Validated E1 configuration has 30 voice channels. |
| `{$E1.CODE.RATE.WARN}` | `0` | `0` alerts on any increase. Tune after observing a healthy baseline. |
| `{$E1.CRC.RATE.WARN}` | `0` | `0` alerts on any increase. Tune after observing a healthy baseline. |
| `{$E1.SLIP.RATE.HIGH}` | `0.1` | Persistent High threshold after 15 minutes. Tune using production history. |
| `{$E1.SLIP.RATE.WARN}` | `0` | `0` alerts on any increase. |
| `{$ICMP.LOSS.WARN}` | `20` | Average packet-loss percentage for Warning. |
| `{$ICMP.RESPONSE.WARN}` | `100` | Average latency in milliseconds for Warning. |
| `{$IF.DISCARD.RATE.WARN}` | `0` | `0` alerts on persistent discard growth. |
| `{$IF.ERROR.RATE.WARN}` | `0` | `0` alerts on persistent interface-error growth. |

The `*.EXPECTED` macros are also used by the configuration/capacity mismatch trigger.

## 8. Validate polling after host creation

After the host is enabled, check **Monitoring → Latest data**.

Confirm that at least these values are populated:

- System description / firmware
- System uptime
- SNMP availability
- ICMP availability/loss/latency
- E1 count and E1 alarm state
- E1 statistics time
- CRC, slips and code violations
- Channel count
- SIP peer count
- Ethernet interfaces and 64-bit RX/TX traffic

Low-level discovery may need one or more discovery/polling cycles before all prototype items become visible.

### Expected channel discovery

For the validated configuration:

```text
Channel 1–15   = voice
Channel 16     = SIG, excluded from voice monitoring
Channel 17–31  = voice
```

The Channel Status Honeycomb should therefore display 30 voice channels.

## 9. Configure SNMP trap reception

The template contains these SNMP trap items:

| Notification | OID | Template behavior |
|---|---|---|
| `e1AlarmsChange` | `1.3.6.1.4.1.41933.1.2.3.1` | Informational trap event; polling remains authoritative for persistent E1 state. |
| `chanStatusChange` | `1.3.6.1.4.1.41933.1.3.3.1` | Informational trap event; polling remains authoritative for persistent channel state. |
| `sipKeepaliveChange` | `1.3.6.1.4.1.41933.1.4.3.1` | Informational trap event. |
| Unmatched traps | `snmptrap.fallback` | Stores traps not matched by the dedicated items. |

The dedicated trap keys match both symbolic notification names and the numeric Aligera OID, so installation of the Aligera MIB is not required for matching. Installing the MIB is still recommended for easier manual troubleshooting and more readable Net-SNMP output.

### 9.1 Enable the Zabbix SNMP trapper

On the Zabbix Server or Proxy that will receive traps, edit the appropriate configuration file:

```text
/etc/zabbix/zabbix_server.conf
```

or:

```text
/etc/zabbix/zabbix_proxy.conf
```

Set:

```ini
StartSNMPTrapper=1
SNMPTrapperFile=/var/lib/zabbix/snmptraps/snmptraps.log
```

Do not place the trap file in `/tmp` on systems where systemd `PrivateTmp` is enabled.

Create the directory:

```bash
mkdir -p /var/lib/zabbix/snmptraps
```

Ensure that the account running the trap handler can append to the file/directory and that the Zabbix Server/Proxy can read it. Service account names differ by distribution, so verify them locally instead of blindly applying ownership values.

### 9.2 Install the official Zabbix Bash trap handler

The Zabbix 7.0 documentation provides a Bash receiver script. Download it:

```bash
curl -L \
  -o /usr/sbin/zabbix_trap_handler.sh \
  https://raw.githubusercontent.com/zabbix/zabbix-docker/7.0/templates/scripts/snmptraps/zabbix_trap_handler.sh

chmod 755 /usr/sbin/zabbix_trap_handler.sh
```

Review the script and make sure its trap-file path matches:

```text
/var/lib/zabbix/snmptraps/snmptraps.log
```

### 9.3 Configure snmptrapd

Edit:

```text
/etc/snmp/snmptrapd.conf
```

For SNMPv2c, replace `TRAP_COMMUNITY` with the community configured on the AG561 trap sender:

```conf
authCommunity log,execute,net TRAP_COMMUNITY
traphandle default /bin/bash /usr/sbin/zabbix_trap_handler.sh
```

The `execute` permission is required for the `traphandle` script.

Restart services:

```bash
systemctl restart snmptrapd
systemctl restart zabbix-server
```

If traps are handled by a Zabbix Proxy instead:

```bash
systemctl restart zabbix-proxy
```

Check service status:

```bash
systemctl --no-pager --full status snmptrapd
systemctl --no-pager --full status zabbix-server
```

or, for a proxy:

```bash
systemctl --no-pager --full status zabbix-proxy
```

Confirm UDP/162 is listening:

```bash
ss -lunp | grep ':162'
```

## 10. Configure traps on the AG561

On each AG561 configure:

- Trap destination: IP of the Zabbix Server or Proxy receiving traps
- Destination port: UDP `162`
- SNMP version: v2c
- Trap community: the community accepted by `snmptrapd`
- Enable the device notifications required for E1, channel and SIP state changes

The exact menu path can vary by AG561 firmware. The template itself does not change the device configuration.

Restrict UDP/162 at the firewall so only authorized AG561 source addresses can send traps to the receiver.

## 11. Validate trap reception

### Packet level

On the trap receiver:

```bash
tcpdump -ni any udp port 162
```

Trigger a controlled state change on the AG561 and confirm that a UDP/162 packet arrives from the expected AG561 source IP.

### Trap-file level

```bash
tail -f /var/lib/zabbix/snmptraps/snmptraps.log
```

A correctly formatted entry used by Zabbix begins with a line containing `ZBXTRAP` followed by the sender address.

Search specifically for Aligera notifications:

```bash
grep -E 'e1AlarmsChange|chanStatusChange|sipKeepaliveChange|41933\.1\.(2\.3\.1|3\.3\.1|4\.3\.1)' \
  /var/lib/zabbix/snmptraps/snmptraps.log
```

### Zabbix level

Check **Monitoring → Latest data** and search for:

- `SNMP trap: E1 alarm state changed`
- `SNMP trap: Channel status changed`
- `SNMP trap: SIP keepalive changed`
- `SNMP traps: Unmatched fallback`

A matching trap creates a short-lived INFO event. Persistent fault severity is determined by the polling triggers.

## 12. Troubleshooting

### Polling does not work

Run:

```bash
snmpget -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.2.1.1.1.0
```

If it fails, verify:

- Community
- Device SNMP service
- UDP/161 firewall path
- Source restrictions on the AG561
- Routing

### Traps do not reach the server

Run:

```bash
tcpdump -ni any udp port 162
```

If no packet arrives, verify:

- AG561 trap destination
- UDP/162 firewall path
- Trap community/version
- Routing

### Packets arrive but nothing is written to the trap file

Check:

```bash
journalctl -u snmptrapd -n 100 --no-pager
cat /etc/snmp/snmptrapd.conf
ls -ld /var/lib/zabbix/snmptraps
ls -l /usr/sbin/zabbix_trap_handler.sh
```

Verify `authCommunity`, `traphandle`, script permissions and trap-file permissions.

### Trap file is populated but Zabbix receives nothing

Check:

```bash
grep -E '^(StartSNMPTrapper|SNMPTrapperFile)=' /etc/zabbix/zabbix_server.conf
```

or the proxy configuration.

Confirm that:

- `StartSNMPTrapper=1`
- `SNMPTrapperFile` exactly matches the handler output file
- Zabbix can read the file
- Zabbix has been restarted after configuration changes
- The host has an SNMP interface
- The selected host-interface IP/DNS matches the trap source address

The last point is especially important: Zabbix first identifies candidate hosts by the received trap address before evaluating the `snmptrap[]` regular expressions.

### Trap appears only in fallback

If an Aligera notification lands in `snmptrap.fallback`, inspect the raw value in Latest data. Check whether the trap contains the symbolic notification or the expected numeric OID.

Expected notification OIDs:

```text
E1:      1.3.6.1.4.1.41933.1.2.3.1
Channel: 1.3.6.1.4.1.41933.1.3.3.1
SIP:     1.3.6.1.4.1.41933.1.4.3.1
```

## 13. Optional Aligera MIB installation

The template polling OIDs are numeric and the trap keys also accept numeric OIDs, so the Aligera MIB is optional for normal operation.

Installing the MIB is recommended for manual `snmpwalk`, `snmptranslate` and more readable trap output. Install the Aligera MIB according to the Net-SNMP MIB directory/configuration used by your operating system and verify it with:

```bash
snmptranslate -On e1AlarmsChange
snmptranslate -On chanStatusChange
snmptranslate -On sipKeepaliveChange
```

## 14. Security recommendations

- Do not use the default `public` community.
- Use dedicated read-only polling and trap communities when the device allows it.
- Restrict UDP/161 to the Zabbix Server/Proxy IPs.
- Restrict UDP/162 to the AG561 source IPs.
- Keep SNMPv2c on trusted private networks only.
- Do not expose UDP/161 or UDP/162 directly to the Internet.
- If a future AG561 firmware supports SNMPv3 for the required monitoring/traps, prefer authentication and encryption.

## 15. Operational validation checklist

After installation confirm:

- [ ] `sysDescr` reports the expected AG561 model/firmware.
- [ ] SNMP availability is green.
- [ ] ICMP data is populated.
- [ ] One E1 is discovered, or `{$AG561.E1.EXPECTED}` was adjusted.
- [ ] 30 voice channels are discovered, or `{$AG561.VOICE.EXPECTED}` was adjusted.
- [ ] TS16/SIG is not shown in the voice-channel Honeycomb.
- [ ] SIP peers match `{$AG561.SIP.EXPECTED}`.
- [ ] Ethernet interfaces are discovered through `ifType=6`.
- [ ] 64-bit traffic counters are updating.
- [ ] E1 quality counters and rates are updating.
- [ ] Capacity mismatch trigger is clear.
- [ ] UDP/162 reaches the intended Zabbix Server/Proxy.
- [ ] Aligera traps are written to the trap file.
- [ ] Dedicated trap items receive matching notifications.
- [ ] `snmptrap.fallback` is available for diagnostics.
- [ ] Threshold macros were reviewed after a representative baseline period.

## References

- Zabbix 7.0 SNMP trap documentation: https://www.zabbix.com/documentation/7.0/en/manual/config/items/itemtypes/snmptrap
- Zabbix 7.0 SNMP monitoring documentation: https://www.zabbix.com/documentation/7.0/en/manual/config/items/itemtypes/snmp
- Original AG562 work by Douglas Boldrini: https://github.com/boldrinidouglas/ZBX-GRA-ALIGERA
