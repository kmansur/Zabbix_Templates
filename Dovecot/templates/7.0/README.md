# Dovecot Template for Zabbix 7.0

Status: 3.0.0 development export.

Import Template_Dovecot_7.0.yaml into Zabbix 7.0 and deploy the current collector from ../../scripts/dovecot_stats.sh with ../../agent/userparameter_dovecot.conf.

The 3.0.0 export preserves existing keys and UUIDs where practical, adds aggregate user-session metrics, uses protocol-aware IMAP/POP3 checks, and introduces response-time recovery hysteresis.

Validate the import diff in homologation before production.
