# Security Policy

## Security principles

Dovecot template 3.0.0 follows least privilege.

- Run dovecot_stats.sh as the unprivileged Zabbix agent user.
- Do not grant sudo permission for dovecot_stats.sh.
- Prefer direct read access to the Dovecot anvil query when the local security model already permits it.
- If privilege escalation is required, permit only the exact read-only command doveadm who -1.
- Keep deployed scripts owned by root and not writable by the Zabbix user.
- Do not store credentials in scripts, templates, macros, fixtures, or examples.
- Do not weaken permissions on Dovecot SQL/authentication files merely to allow checksum monitoring.
- Keep the Dovecot statistics output aggregate-only; do not add usernames, client IPs, or mailbox names to Zabbix items without an explicit privacy and operational requirement.

## Sudoers

Supported examples are stored in agent/sudoers.d/.

Validate changes with visudo -cf before installation.

Avoid:

- ALL command grants.
- unrestricted doveadm grants.
- SETENV unless there is a separately reviewed requirement.
- running the whole collector as root.

## Reporting a security issue

Do not publish credentials, production configuration, customer data, or exploit details in a public issue.

Open a minimal report without secrets and coordinate sensitive evidence privately with the repository owner.
