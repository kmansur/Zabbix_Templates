# Contributing

## Rules

- Keep Zabbix 7.0 and 8.0 exports aligned.
- Preserve existing item keys and UUIDs unless a documented breaking change is necessary.
- Do not remove legacy files without a documented migration path.
- Keep English and Brazilian Portuguese documentation synchronized.
- Keep production collector code POSIX shell compatible.
- Do not add a production runtime dependency unless it provides a clear operational benefit.
- Follow least privilege. Never solve a monitoring limitation by granting broad root access.
- Avoid hardcoded trigger thresholds when a template macro is appropriate.
- Do not expose usernames, client IPs, credentials, or mailbox names in aggregate monitoring items.
- Test changes in homologation before production.

## Before opening a pull request

~~~sh
sh -n scripts/dovecot_stats.sh
sh tests/test_dovecot_stats.sh
python3 tests/validate_templates.py
~~~

Also:

1. Import templates/7.0/Template_Dovecot_7.0.yaml into a Zabbix 7.0 test environment.
2. Import templates/8.0/Template_Dovecot_8.0.yaml into a Zabbix 8.0 test environment.
3. Review the import diff for unintended object recreation or deletion.
4. Validate the collector on at least one target operating system.
5. Update CHANGELOG.md and CHANGELOG.pt-BR.md for user-visible changes.
