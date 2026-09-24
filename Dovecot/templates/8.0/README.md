# Dovecot Template for Zabbix 8.0

Status: 3.0.0 development export.

Import Template_Dovecot_8.0.yaml into Zabbix 8.0 and deploy the current collector from ../../scripts/dovecot_stats.sh with ../../agent/userparameter_dovecot.conf.

The 3.0.0 export preserves existing keys and UUIDs where practical, adds aggregate user-session metrics, uses protocol-aware IMAP/POP3 checks, and introduces response-time recovery hysteresis.

The export is covered by static YAML, key, UUID, macro, and regression checks. Validate the import in a Zabbix 8.0 homologation environment before production use.
