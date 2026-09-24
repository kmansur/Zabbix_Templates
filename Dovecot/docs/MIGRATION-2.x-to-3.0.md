# Migration from Dovecot Template 2.x to 3.0.0

Version 3.0.0 is intentionally structured as a major upgrade because it changes the collector deployment layout and the privilege model.

## What is preserved

The existing template name, principal UUIDs, and existing item keys are preserved whenever practical.

The following monitoring data remains available:

- Collector status and error.
- IMAP connections.
- POP3 connections.
- Total connections.
- Dovecot version.
- Dovecot master process.
- IMAP, IMAPS, POP3, and POP3S availability.
- Service response time.
- Main and SQL configuration checksums.
- Existing graphs and threshold macros.

## What is added

- dovecot.collector.version
- dovecot.connections.users
- dovecot.connections.max_per_user
- Response-time recovery hysteresis.
- Protocol-aware IMAP and POP3 checks.
- FreeBSD/Linux executable path detection.
- CI/static validation.

## Repository layout change

2.x stored the current collector and UserParameter in the Dovecot project root.

3.0.0 uses:

~~~text
scripts/dovecot_stats.sh
agent/userparameter_dovecot.conf
agent/sudoers.d/
~~~

The deployed collector path remains:

~~~text
/usr/local/scripts/dovecot_stats.sh
~~~

so the host-side script location does not need to change.

## Important sudo change

2.x documentation granted sudo to the collector script.

Do not keep this rule:

~~~text
zabbix ALL=(root) NOPASSWD: /usr/local/scripts/dovecot_stats.sh
~~~

3.0.0 runs the script unprivileged and, if required, allows only the exact Dovecot query.

FreeBSD:

~~~text
zabbix ALL=(root) NOPASSWD: /usr/local/bin/doveadm who -1
~~~

Linux:

~~~text
zabbix ALL=(root) NOPASSWD: /usr/bin/doveadm who -1
~~~

Before changing sudoers, test whether the zabbix user can already run doveadm who -1 directly. If direct access works, do not add a sudo rule.

## Recommended migration order

1. Export or back up the existing Zabbix template configuration.
2. Copy scripts/dovecot_stats.sh to /usr/local/scripts/dovecot_stats.sh.
3. Install agent/userparameter_dovecot.conf.
4. Test direct doveadm access as zabbix.
5. If required, install the exact-command sudoers rule.
6. Remove the old rule that grants root execution of dovecot_stats.sh.
7. Restart the Zabbix agent.
8. Test dovecot.stats, dovecot.version, and dovecot.collector.version locally.
9. Import the matching 3.0.0 template into homologation.
10. Review the import diff before applying it in production.
11. Confirm existing item history remains associated with the updated template items.
12. Keep the 2.x files available until the new collection is stable.

## Service key changes

Plain IMAP and POP3 checks now use protocol-aware service types.

Conceptually:

~~~text
IMAP: tcp -> imap
POP3: tcp -> pop
~~~

IMAPS and POP3S remain TCP checks.

Because the existing item UUIDs are preserved, the template import is intended to update the existing items rather than create parallel items. Always verify the actual import preview in the target Zabbix version.

## Rollback

To roll back:

1. Restore the previous collector file.
2. Restore the previous UserParameter configuration.
3. Restore the previous sudoers rule only if the old collector requires it.
4. Re-import the previous template export with delete-missing disabled unless you explicitly intend to remove 3.0-only items.
5. Restart the Zabbix agent and validate the original keys.
