# Validation Checklist

Use this checklist before importing the template into production.

## Static checks

```bash
sh -n dovecot_stats.sh
sh -n legacy/zabbix-5.0/dovecot_num_imap.sh
sh -n legacy/zabbix-5.0/dovecot_num_pop.sh
python3 - <<'PYCODE'
import yaml
with open('templates/7.0/Template_Dovecot_7.0.yaml', 'r', encoding='utf-8') as f:
    yaml.safe_load(f)
print('YAML syntax OK')
PYCODE
```

## Local parser test

```bash
sh tests/test_dovecot_stats.sh
```

Expected result:

```text
OK: dovecot_stats.sh parser test passed
```

## Host checks

```bash
doveadm who
doveadm who -1
sudo -u zabbix sudo -n /usr/local/scripts/dovecot_stats.sh
sudo -u zabbix /usr/local/sbin/zabbix_agentd -t dovecot.stats
sudo -u zabbix /usr/local/sbin/zabbix_agentd -t dovecot.version
```

## Zabbix import checks

1. Import `templates/7.0/Template_Dovecot_7.0.yaml` in homologation first.
2. Link the template to one Dovecot host.
3. Check Latest data for `dovecot.stats`, collector items, connection items, process item, service availability items, and service response-time items.
4. Confirm that TCP service items return `Up`.
5. Confirm that the `Dovecot connections` graph shows IMAP, POP3, and total connections.
6. Confirm that the `Dovecot service response time` graph shows IMAP, IMAPS, POP3, and POP3S response times.
7. Tune host-level macros before production use.

## Production notes

- Do not enable delete-missing import options without reviewing the import diff.
- Tune connection thresholds per server capacity.
- IMAPS and POP3S validate TCP connectivity only.
- Keep scripts owned by root and writable only by trusted administrators.
