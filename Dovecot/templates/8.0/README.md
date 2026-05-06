# Dovecot Template for Zabbix 8.0

Status: export present, statically validated.

Import `Template_Dovecot_8.0.yaml` into Zabbix 8.0 and use the root `dovecot_stats.sh` and `userparameter_dovecot.conf` files on monitored Dovecot hosts.

This export has been checked for YAML syntax, duplicate UUIDs, missing macros, and parity with the Zabbix 7.0 monitored item/macro/graph surface. Validate the import in a Zabbix 8.0 homologation environment before production use.
