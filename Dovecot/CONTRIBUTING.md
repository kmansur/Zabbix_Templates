# Contributing

## Rules

- Keep compatibility with Zabbix 7.0.
- Do not remove legacy files without a documented migration path.
- Keep English and Portuguese documentation synchronized.
- Keep scripts POSIX shell compatible.
- Avoid hardcoded thresholds in triggers. Use template macros.
- Test changes in homologation before production.

## Before opening a pull request

```bash
sh -n dovecot_stats.sh
sh -n dovecot_num_imap.sh
sh -n dovecot_num_pop.sh
sh tests/test_dovecot_stats.sh
```

Also import `Template_Dovecot_7.0.yaml` into a Zabbix 7.0 test environment and check the import diff.
