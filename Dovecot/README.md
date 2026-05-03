# Dovecot Zabbix Template

Portuguese version: [README.pt-BR.md](README.pt-BR.md)

> Production version: 1.0.0
>
> Documentation maintenance: when this English README is updated, update
> `README.pt-BR.md` in the same change.

Zabbix template project for basic Dovecot monitoring. This version is based on
a production deployment using FreeBSD paths and Zabbix 5.0 template format.

## Files

- `Template_App_Dovecot.xml`: Zabbix template export.
- `dovecot_num_imap.sh`: counts active IMAP sessions from `doveadm who`.
- `dovecot_num_pop.sh`: counts active POP3 sessions from `doveadm who`.
- `dovecot_stats.sh`: returns IMAP, POP3, and total session counters as CSV.
- `userparameter_dovecot.conf`: Zabbix agent UserParameter definitions.
- `CHANGELOG.md`: English changelog.
- `CHANGELOG.pt-BR.md`: Portuguese changelog.

## Monitored Data

- Active IMAP connections.
- Active POP3 connections.
- Dovecot version.
- IMAP service availability.
- POP3 service availability.
- IMAPS service availability on TCP port 993.
- POP3S service availability on TCP port 995.
- Checksum changes for selected Dovecot configuration files.

## Requirements

- Zabbix server compatible with template export version 5.0.
- Zabbix agent installed on the Dovecot host.
- Dovecot installed with `doveadm` available.
- FreeBSD-style paths, unless adjusted manually.
- `sudo` access for the Zabbix agent user to run the Dovecot session scripts.

Default paths used by this version:

```text
/usr/local/bin/doveadm
/usr/local/sbin/dovecot
/usr/local/scripts/
/usr/local/etc/dovecot/
```

For Linux or other operating systems, adjust script paths, UserParameters, and
configuration file checksum items as needed.

## Installation

1. Copy the scripts to the monitored host:

   ```bash
   cp dovecot_num_imap.sh /usr/local/scripts/
   cp dovecot_num_pop.sh /usr/local/scripts/
   cp dovecot_stats.sh /usr/local/scripts/
   chmod 755 /usr/local/scripts/dovecot_num_imap.sh
   chmod 755 /usr/local/scripts/dovecot_num_pop.sh
   chmod 755 /usr/local/scripts/dovecot_stats.sh
   ```

2. Copy the UserParameter file to the Zabbix agent include directory:

   ```bash
   cp userparameter_dovecot.conf /usr/local/etc/zabbix_agentd.conf.d/
   ```

3. Configure `sudo` for the Zabbix agent user according to your local security
   policy. The current UserParameters call the session scripts through `sudo`.

4. Restart the Zabbix agent.

5. Import `Template_App_Dovecot.xml` into Zabbix.

6. Link `Template App Dovecot` to the Dovecot host.

## Template Macros

| Macro | Default | Description |
| --- | ---: | --- |
| `{$IMAP.WARN}` | `200` | Warning threshold for active IMAP connections. |
| `{$IMAP.HIGH}` | `350` | High threshold for active IMAP connections. |
| `{$POP.WARN}` | `200` | Warning threshold for active POP3 connections. |
| `{$POP.HIGH}` | `350` | High threshold for active POP3 connections. |

Adjust these macros per host or host group to match the expected workload.

## Notes

- This 1.0.0 version intentionally preserves the production behavior of the
  existing template and scripts.
- The repository layout was reorganized so the template, scripts,
  UserParameter file, README files, and changelogs live in the same directory.
- Future versions may modernize the collection method, triggers, macros, and
  template format.
