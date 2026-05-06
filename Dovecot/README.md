# Dovecot Zabbix Template

Portuguese version: [README.pt-BR.md](README.pt-BR.md)

> Development version: 2.0.0
>
> Documentation maintenance: when this English README is updated, update `README.pt-BR.md` in the same change.

Zabbix template project for monitoring Dovecot through Zabbix agent UserParameters. Version 2.0.0 adds a Zabbix 7.0 YAML template, JSON-based collection, dependent items, service enable macros, port macros, recovery macros, process monitoring, service response-time checks, value mapping, graphs, and validation documentation while keeping the 1.0.0 XML template available for reference.

## Files

- `Template_Dovecot_7.0.yaml`: Zabbix 7.0 template export for version 2.0.0.
- `dovecot_stats.sh`: JSON master collection script for Dovecot sessions.
- `userparameter_dovecot.conf`: Zabbix agent UserParameter definitions.
- `legacy/zabbix-5.0/`: legacy Zabbix 5.0 XML template, legacy IMAP/POP3 counters, and matching UserParameter file.
- `docs/VALIDATION.md`: validation and pre-production checklist.
- `tests/test_dovecot_stats.sh`: local parser test for the collector scripts.
- `CHANGELOG.md`: English changelog.
- `CHANGELOG.pt-BR.md`: Portuguese changelog.

## Monitored Data

- Dovecot collector availability and last error.
- Active IMAP connections.
- Active POP3 connections.
- Total active IMAP and POP3 connections.
- Dovecot master process count.
- Dovecot version.
- IMAP, IMAPS, POP3, and POP3S TCP service availability.
- IMAP, IMAPS, POP3, and POP3S TCP service response time.
- Checksum changes for selected Dovecot configuration files.

## Requirements

- Zabbix server compatible with template export version 7.0.
- Zabbix agent installed on the Dovecot host.
- Dovecot installed with `doveadm` available.
- `sudo` access for the Zabbix agent user to run the Dovecot session scripts.

Default paths used by this version:

```text
/usr/local/bin/doveadm
/usr/local/sbin/dovecot
/usr/local/scripts/
/usr/local/etc/dovecot/
```

The scripts support `DOVECOT_DOVEADM` as an environment override for the `doveadm` path. When scripts run through `sudo -n`, your sudoers policy might not preserve environment variables.

## Installation

1. Copy `dovecot_stats.sh` to `/usr/local/scripts/` and set mode `755`.
2. Restrict ownership:

   ```bash
   # FreeBSD
   chown root:wheel /usr/local/scripts/dovecot_stats.sh

   # Linux
   chown root:root /usr/local/scripts/dovecot_stats.sh
   ```

3. Copy `userparameter_dovecot.conf` to the Zabbix agent include directory.
4. Configure sudoers:

   ```text
   zabbix ALL=(root) NOPASSWD: /usr/local/scripts/dovecot_stats.sh
   ```

5. Restart the Zabbix agent.
6. Import `Template_Dovecot_7.0.yaml` into Zabbix 7.0.
7. Link `Template App Dovecot` to the Dovecot host.

## Validation

```bash
sh -n /usr/local/scripts/dovecot_stats.sh
sudo -u zabbix sudo -n /usr/local/scripts/dovecot_stats.sh
sudo -u zabbix zabbix_agentd -t dovecot.stats
sudo -u zabbix zabbix_agentd -t dovecot.version
```

More checks are available in `docs/VALIDATION.md`.

## Script Output

```json
{"status":1,"imap":10,"pop3":2,"total":12,"error":""}
```

If collection fails:

```json
{"status":0,"imap":0,"pop3":0,"total":0,"error":"doveadm_who_failed"}
```

## Counting Method

Version 2.0.0 uses:

```bash
doveadm who -1
```

This avoids undercounting when `doveadm who` groups several connections from the same user into one line.

## Template Macros

| Macro | Default | Description |
| --- | ---: | --- |
| `{$DOVECOT.IMAP.CONN.WARN}` | `200` | Warning threshold for average active IMAP connections. |
| `{$DOVECOT.IMAP.CONN.WARN.RECOVERY}` | `180` | Recovery threshold for IMAP warning connection trigger. |
| `{$DOVECOT.IMAP.CONN.HIGH}` | `350` | High threshold for average active IMAP connections. |
| `{$DOVECOT.IMAP.CONN.HIGH.RECOVERY}` | `320` | Recovery threshold for IMAP high connection trigger. |
| `{$DOVECOT.POP3.CONN.WARN}` | `200` | Warning threshold for average active POP3 connections. |
| `{$DOVECOT.POP3.CONN.WARN.RECOVERY}` | `180` | Recovery threshold for POP3 warning connection trigger. |
| `{$DOVECOT.POP3.CONN.HIGH}` | `350` | High threshold for average active POP3 connections. |
| `{$DOVECOT.POP3.CONN.HIGH.RECOVERY}` | `320` | Recovery threshold for POP3 high connection trigger. |
| `{$DOVECOT.TOTAL.CONN.WARN}` | `350` | Warning threshold for average active IMAP and POP3 connections. |
| `{$DOVECOT.TOTAL.CONN.WARN.RECOVERY}` | `320` | Recovery threshold for total connection warning trigger. |
| `{$DOVECOT.TOTAL.CONN.HIGH}` | `600` | High threshold for average active IMAP and POP3 connections. |
| `{$DOVECOT.TOTAL.CONN.HIGH.RECOVERY}` | `550` | Recovery threshold for total connection high trigger. |
| `{$DOVECOT.SERVICE.RESPONSE.WARN}` | `2` | Warning threshold in seconds for TCP service response time. |
| `{$DOVECOT.IMAP.ENABLED}` | `1` | Set to `0` to disable IMAP service availability triggers. |
| `{$DOVECOT.IMAPS.ENABLED}` | `1` | Set to `0` to disable IMAPS service availability triggers. |
| `{$DOVECOT.POP3.ENABLED}` | `1` | Set to `0` to disable POP3 service availability triggers. |
| `{$DOVECOT.POP3S.ENABLED}` | `1` | Set to `0` to disable POP3S service availability triggers. |
| `{$DOVECOT.IMAP.PORT}` | `143` | IMAP TCP port. |
| `{$DOVECOT.IMAPS.PORT}` | `993` | IMAPS TCP port. |
| `{$DOVECOT.POP3.PORT}` | `110` | POP3 TCP port. |
| `{$DOVECOT.POP3S.PORT}` | `995` | POP3S TCP port. |
| `{$DOVECOT.PROCESS.NAME}` | `dovecot` | Dovecot master process name used by `proc.num[]`. |
| `{$DOVECOT.CONF.FILE}` | `/usr/local/etc/dovecot/dovecot.conf` | Main Dovecot configuration file to checksum. |
| `{$DOVECOT.SQL.CONF.FILE}` | `/usr/local/etc/dovecot/dovecot-mysql.conf` | SQL authentication configuration file to checksum. |

## Compatibility Notes

- `Template_Dovecot_7.0.yaml` is the main template for version 2.0.0.
- `legacy/zabbix-5.0/Template_App_Dovecot.xml` is kept as the version 1.0.0 legacy template.
- `legacy/zabbix-5.0/dovecot_num_imap.sh`, `legacy/zabbix-5.0/dovecot_num_pop.sh`, and `legacy/zabbix-5.0/userparameter_dovecot_legacy.conf` preserve the `dovecot.imap` and `dovecot.pop` keys for Zabbix 5.0 deployments.
- IMAPS and POP3S checks validate TCP connectivity only. They do not validate TLS negotiation or authentication.
