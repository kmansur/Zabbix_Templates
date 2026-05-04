# Dovecot Zabbix Template

Portuguese version: [README.pt-BR.md](README.pt-BR.md)

> Development version: 2.0.0
>
> Documentation maintenance: when this English README is updated, update
> `README.pt-BR.md` in the same change.

Zabbix template project for monitoring Dovecot through Zabbix agent
UserParameters. Version 2.0.0 adds a Zabbix 7.0 YAML template, JSON-based
collection, dependent items, service enable macros, port macros, and improved
documentation while keeping the 1.0.0 XML template available for reference.

## Files

- `Template_Dovecot_7.0.yaml`: Zabbix 7.0 template export for version 2.0.0.
- `Template_App_Dovecot.xml`: legacy Zabbix 5.0 XML template from version 1.0.0.
- `dovecot_stats.sh`: JSON master collection script for Dovecot sessions.
- `dovecot_num_imap.sh`: legacy-compatible IMAP session counter.
- `dovecot_num_pop.sh`: legacy-compatible POP3 session counter.
- `userparameter_dovecot.conf`: Zabbix agent UserParameter definitions.
- `CHANGELOG.md`: English changelog.
- `CHANGELOG.pt-BR.md`: Portuguese changelog.

## Monitored Data

- Dovecot collector availability and last error.
- Active IMAP connections.
- Active POP3 connections.
- Total active IMAP and POP3 connections.
- Dovecot version.
- IMAP service availability.
- IMAPS service availability.
- POP3 service availability.
- POP3S service availability.
- Checksum changes for selected Dovecot configuration files.

## Requirements

- Zabbix server compatible with template export version 7.0.
- Zabbix agent installed on the Dovecot host.
- Dovecot installed with `doveadm` available.
- `sudo` access for the Zabbix agent user to run the Dovecot session script.

Default paths used by this version:

```text
/usr/local/bin/doveadm
/usr/local/sbin/dovecot
/usr/local/scripts/
/usr/local/etc/dovecot/
```

The scripts support `DOVECOT_DOVEADM` as an environment override for the
`doveadm` path. For Linux or other operating systems, adjust script paths,
UserParameters, and configuration file macros as needed.

## Installation

1. Copy the scripts to the monitored host:

   ```bash
   cp dovecot_stats.sh /usr/local/scripts/
   cp dovecot_num_imap.sh /usr/local/scripts/
   cp dovecot_num_pop.sh /usr/local/scripts/
   chmod 755 /usr/local/scripts/dovecot_stats.sh
   chmod 755 /usr/local/scripts/dovecot_num_imap.sh
   chmod 755 /usr/local/scripts/dovecot_num_pop.sh
   ```

2. Copy the UserParameter file to the Zabbix agent include directory:

   ```bash
   cp userparameter_dovecot.conf /usr/local/etc/zabbix_agentd.conf.d/
   ```

3. Configure `sudo` for the Zabbix agent user. The UserParameters use
   `sudo -n`, so missing permissions fail quickly instead of waiting for a
   password prompt.

   Example sudoers rule:

   ```text
   zabbix ALL=(root) NOPASSWD: /usr/local/scripts/dovecot_stats.sh, /usr/local/scripts/dovecot_num_imap.sh, /usr/local/scripts/dovecot_num_pop.sh
   ```

4. Restart the Zabbix agent.

5. Import `Template_Dovecot_7.0.yaml` into Zabbix 7.0.

6. Link `Template App Dovecot` to the Dovecot host.

## Script Output

`dovecot_stats.sh` returns JSON for the Zabbix master item:

```json
{"status":1,"imap":10,"pop3":2,"total":12,"error":""}
```

If collection fails, the script still returns valid JSON:

```json
{"status":0,"imap":0,"pop3":0,"total":0,"error":"doveadm_who_failed"}
```

## Template Macros

| Macro | Default | Description |
| --- | ---: | --- |
| `{$DOVECOT.IMAP.CONN.WARN}` | `200` | Warning threshold for average active IMAP connections. |
| `{$DOVECOT.IMAP.CONN.HIGH}` | `350` | High threshold for average active IMAP connections. |
| `{$DOVECOT.POP3.CONN.WARN}` | `200` | Warning threshold for average active POP3 connections. |
| `{$DOVECOT.POP3.CONN.HIGH}` | `350` | High threshold for average active POP3 connections. |
| `{$DOVECOT.IMAP.ENABLED}` | `1` | Set to `0` to disable IMAP service availability triggers. |
| `{$DOVECOT.IMAPS.ENABLED}` | `1` | Set to `0` to disable IMAPS service availability triggers. |
| `{$DOVECOT.POP3.ENABLED}` | `1` | Set to `0` to disable POP3 service availability triggers. |
| `{$DOVECOT.POP3S.ENABLED}` | `1` | Set to `0` to disable POP3S service availability triggers. |
| `{$DOVECOT.IMAP.PORT}` | `143` | IMAP TCP port. |
| `{$DOVECOT.IMAPS.PORT}` | `993` | IMAPS TCP port. |
| `{$DOVECOT.POP3.PORT}` | `110` | POP3 TCP port. |
| `{$DOVECOT.POP3S.PORT}` | `995` | POP3S TCP port. |
| `{$DOVECOT.CONF.FILE}` | `/usr/local/etc/dovecot/dovecot.conf` | Main Dovecot configuration file to checksum. |
| `{$DOVECOT.SQL.CONF.FILE}` | `/usr/local/etc/dovecot/dovecot-mysql.conf` | SQL authentication configuration file to checksum. |

## Compatibility Notes

- `Template_Dovecot_7.0.yaml` is the main template for version 2.0.0.
- `Template_App_Dovecot.xml` is kept as the version 1.0.0 legacy template.
- `dovecot.imap` and `dovecot.pop` UserParameters are preserved for legacy
  compatibility.
- New Zabbix 7.0 items should use `dovecot.stats` as the master item.
