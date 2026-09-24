# Dovecot Zabbix Template

Portuguese version: [README.pt-BR.md](README.pt-BR.md)

> Development version: 3.0.0
>
> Status: development branch. Validate in homologation before production.
>
> Documentation maintenance: when this English README is updated, update README.pt-BR.md in the same change.

Zabbix template project for monitoring Dovecot with a small POSIX shell collector and Zabbix agent UserParameters. Version 3.0.0 keeps the existing monitoring surface and history-compatible keys/UUIDs while improving privilege separation, portability, protocol validation, regression testing, and operational visibility.

## Design goals

- Preserve existing Dovecot metrics and template identifiers whenever possible.
- Keep the collector small, auditable, POSIX-shell compatible, and dependency-free.
- Run the collector as the unprivileged Zabbix agent user.
- Escalate only the exact read-only command doveadm who -1 when access to the Dovecot anvil socket requires it.
- Prefer one JSON master collection with dependent items.
- Avoid storing usernames or addresses in Zabbix.
- Support the common FreeBSD and Linux Dovecot paths.
- Keep Zabbix 7.0 and 8.0 exports aligned.

## Repository layout

- templates/7.0/Template_Dovecot_7.0.yaml - Zabbix 7.0 export.
- templates/8.0/Template_Dovecot_8.0.yaml - Zabbix 8.0 export.
- templates/6.0/ - reserved for a future validated Zabbix 6.0 export.
- scripts/dovecot_stats.sh - current JSON collector.
- agent/userparameter_dovecot.conf - current UserParameter configuration.
- agent/sudoers.d/ - least-privilege sudoers examples for FreeBSD and Linux.
- docs/VALIDATION.md - static, host, import, and production checks.
- docs/MIGRATION-2.x-to-3.0.md - migration notes for existing installations.
- tests/test_dovecot_stats.sh - collector regression tests.
- tests/validate_templates.py - static YAML/template consistency validator.
- legacy/zabbix-5.0/ - preserved Zabbix 5.0 template and legacy scripts.

## Monitored data

Version 3.0.0 preserves the existing monitored data:

- Collector availability and last error.
- Active IMAP connections.
- Active POP3 connections.
- Total active IMAP and POP3 connections.
- Dovecot master process count.
- Dovecot version.
- IMAP, IMAPS, POP3, and POP3S service availability.
- IMAP, IMAPS, POP3, and POP3S service response time.
- Checksum changes for selected Dovecot configuration files.

It also adds:

- Number of unique users with active IMAP/POP3 sessions.
- Maximum active IMAP/POP3 connections observed for a single user.
- Collector version.

The collector never sends usernames to Zabbix. Usernames are used only in memory to calculate aggregate counters.

## Collection architecture

The master key is:

~~~text
dovecot.stats
~~~

Example output:

~~~json
{"status":1,"imap":10,"pop3":2,"total":12,"users":8,"max_user_connections":3,"error":""}
~~~

If collection fails:

~~~json
{"status":0,"imap":0,"pop3":0,"total":0,"users":0,"max_user_connections":0,"error":"doveadm_who_failed"}
~~~

The collector uses doveadm who -1. Dovecot documents -1 as one output line per user and connection, preventing undercounting when a user has multiple simultaneous connections.

## Security model

The collector must run as the Zabbix agent user. Do not grant sudo permission for the collector script.

The collector first executes:

~~~text
doveadm who -1
~~~

without privilege escalation. If the Zabbix user cannot query the Dovecot anvil socket, it retries only the same command through sudo -n.

FreeBSD example:

~~~text
zabbix ALL=(root) NOPASSWD: /usr/local/bin/doveadm who -1
~~~

Linux example:

~~~text
zabbix ALL=(root) NOPASSWD: /usr/bin/doveadm who -1
~~~

Do not replace these rules with unrestricted doveadm access and do not grant NOPASSWD permission to dovecot_stats.sh.

See SECURITY.md for additional guidance.

## Requirements

- Zabbix 7.0 or 8.0 matching the chosen export.
- Zabbix agent or agent 2 on the Dovecot host.
- Dovecot with doveadm available.
- POSIX shell and awk.
- sudo only when the Zabbix user cannot query the Dovecot anvil socket directly.

Common paths detected automatically:

~~~text
FreeBSD
/usr/local/bin/doveadm
/usr/local/sbin/dovecot

Linux
/usr/bin/doveadm
/usr/sbin/dovecot
~~~

## Installation

1. Install the collector:

~~~sh
install -o root -g wheel -m 0755 scripts/dovecot_stats.sh /usr/local/scripts/dovecot_stats.sh
~~~

On Linux, use the appropriate root group for the distribution.

2. Install agent/userparameter_dovecot.conf in the Zabbix agent include directory.

3. Test direct access first:

~~~sh
sudo -u zabbix /usr/local/bin/doveadm who -1
~~~

or on Linux:

~~~sh
sudo -u zabbix /usr/bin/doveadm who -1
~~~

4. Only if direct access fails because of socket permissions, install the matching sudoers example and validate it with visudo -cf.

5. Restart the Zabbix agent.

6. Validate the keys:

~~~sh
sudo -u zabbix zabbix_agentd -t dovecot.stats
sudo -u zabbix zabbix_agentd -t dovecot.version
sudo -u zabbix zabbix_agentd -t dovecot.collector.version
~~~

7. Import the matching YAML template and link Template App Dovecot to the host.

## Service checks

Plain IMAP and POP3 use protocol-aware Zabbix checks:

~~~text
net.tcp.service[imap,...]
net.tcp.service[pop,...]
~~~

IMAPS and POP3S remain TCP-level checks because Zabbix agent service checks do not perform IMAPS/POP3S negotiation on ports 993/995.

## Configuration checksum items

The main and SQL configuration checksum items are preserved from 2.x.

Do not weaken file permissions only to make a checksum item work. If the Zabbix agent cannot safely read a protected configuration file, disable that item for the host or use a deliberately designed integrity-monitoring method.

## Compatibility

| Component | Status |
| --- | --- |
| Zabbix 7.0 | Template export maintained |
| Zabbix 8.0 | Template export maintained |
| Zabbix 6.0 | Planned, not validated |
| Dovecot 2.3 | Collector design compatible; validate on target host |
| Dovecot 2.4 | Collector design compatible; validate on target host |
| FreeBSD | Supported path layout |
| Linux | Supported common path layout |

## Upgrade from 2.x

Version 3.0.0 reorganizes the project into scripts/ and agent/ directories and changes the sudo model. Existing template keys and UUIDs are preserved where practical so an import updates the template instead of creating parallel items.

Read docs/MIGRATION-2.x-to-3.0.md before upgrading an existing host.

## Validation

Run:

~~~sh
sh -n scripts/dovecot_stats.sh
sh tests/test_dovecot_stats.sh
python3 tests/validate_templates.py
~~~

The Python validator requires PyYAML and is intended for development/CI only. The monitored host does not require Python.

See docs/VALIDATION.md for the complete checklist.

## License

This project is licensed under the MIT License. See LICENSE.
