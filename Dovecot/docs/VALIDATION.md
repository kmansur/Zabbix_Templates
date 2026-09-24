# Validation Checklist

Use this checklist before importing Dovecot template 3.0.0 into production.

## 1. Static checks

From the Dovecot project directory:

~~~sh
sh -n scripts/dovecot_stats.sh
sh tests/test_dovecot_stats.sh
python3 tests/validate_templates.py
~~~

The Python validator requires PyYAML only in the development/CI environment.

It checks:

- YAML syntax.
- Export version.
- Template vendor version.
- Required keys.
- Duplicate UUIDs inside each export.
- Undefined user macros.
- Protocol-aware IMAP and POP3 checks.

## 2. File ownership

The deployed collector must be administrator-owned and not writable by the Zabbix agent user.

FreeBSD example:

~~~sh
chown root:wheel /usr/local/scripts/dovecot_stats.sh
chmod 0755 /usr/local/scripts/dovecot_stats.sh
ls -l /usr/local/scripts/dovecot_stats.sh
~~~

Linux example:

~~~sh
chown root:root /usr/local/scripts/dovecot_stats.sh
chmod 0755 /usr/local/scripts/dovecot_stats.sh
ls -l /usr/local/scripts/dovecot_stats.sh
~~~

## 3. Dovecot access

Determine the local path first.

FreeBSD:

~~~sh
/usr/local/bin/doveadm who -1
~~~

Linux:

~~~sh
/usr/bin/doveadm who -1
~~~

Test as the Zabbix user without sudo.

FreeBSD:

~~~sh
sudo -u zabbix /usr/local/bin/doveadm who -1
~~~

Linux:

~~~sh
sudo -u zabbix /usr/bin/doveadm who -1
~~~

If this succeeds, no sudo rule is required for collection.

If it fails because the Zabbix user cannot access the Dovecot anvil socket, install only the matching least-privilege rule from agent/sudoers.d/.

Validate the candidate sudoers file before installation:

~~~sh
visudo -cf agent/sudoers.d/zabbix-dovecot.freebsd
~~~

or:

~~~sh
visudo -cf agent/sudoers.d/zabbix-dovecot.linux
~~~

Never grant sudo for dovecot_stats.sh itself.

## 4. Collector checks

Run the collector as the Zabbix user:

~~~sh
sudo -u zabbix /usr/local/scripts/dovecot_stats.sh stats
sudo -u zabbix /usr/local/scripts/dovecot_stats.sh version
sudo -u zabbix /usr/local/scripts/dovecot_stats.sh collector-version
~~~

Expected JSON shape:

~~~json
{"status":1,"imap":10,"pop3":2,"total":12,"users":8,"max_user_connections":3,"error":""}
~~~

Confirm:

- status is 1.
- total equals imap plus pop3.
- users does not exceed total when total is greater than zero.
- max_user_connections is zero when no IMAP/POP3 session exists.
- no username is present in the JSON output.

## 5. Zabbix agent checks

Use the installed agent binary for the target platform.

Examples:

~~~sh
sudo -u zabbix zabbix_agentd -t dovecot.stats
sudo -u zabbix zabbix_agentd -t dovecot.version
sudo -u zabbix zabbix_agentd -t dovecot.collector.version
~~~

or with agent 2:

~~~sh
sudo -u zabbix zabbix_agent2 -t dovecot.stats
sudo -u zabbix zabbix_agent2 -t dovecot.version
sudo -u zabbix zabbix_agent2 -t dovecot.collector.version
~~~

## 6. Zabbix import checks

1. Import the matching export in homologation first.
2. Review the import diff.
3. Do not enable delete-missing options without reviewing every removal.
4. Confirm that existing Dovecot keys are updated instead of duplicated.
5. Link the template to one test host.
6. Check Latest data for:
   - dovecot.stats
   - dovecot.collector.available
   - dovecot.collector.error
   - dovecot.collector.version
   - dovecot.connections.imap
   - dovecot.connections.pop3
   - dovecot.connections.total
   - dovecot.connections.users
   - dovecot.connections.max_per_user
   - dovecot.version
   - process monitoring
   - service availability
   - service response time
   - configuration checksum items
7. Confirm that the Dovecot connections graph contains the preserved counters and the new aggregate user counters.
8. Tune host-level threshold macros for the actual server capacity.

## 7. Service validation

For plain IMAP and POP3, the template performs protocol-aware checks.

For IMAPS and POP3S, the template validates TCP connectivity because encrypted IMAP/POP3 negotiation is not supported by these Zabbix agent service checks.

A successful local service check does not prove external client reachability through NAT, firewall, load balancer, or security policy. Use a Zabbix server/proxy simple check separately when external reachability must also be monitored.

## 8. Configuration checksum safety

Do not change protected Dovecot configuration file permissions merely to satisfy vfs.file.cksum.

If the SQL configuration contains credentials and is intentionally unreadable by the Zabbix user, disable the checksum item for that host or use a separate integrity-monitoring mechanism designed around least privilege.

## 9. Production acceptance

Before enabling production alerting:

- Confirm the collector remains below the Zabbix agent item timeout.
- Confirm no sudo password prompt occurs.
- Confirm the exact sudo rule works and broader doveadm commands remain denied.
- Confirm service enable macros match the protocols actually enabled on the host.
- Confirm connection thresholds match the normal baseline.
- Confirm the SQL checksum item does not require weaker file permissions.
- Keep the 2.x deployment files available for rollback until 3.0.0 is accepted.
