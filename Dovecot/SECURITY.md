# Security Policy

## Security notes

- The Zabbix agent user needs passwordless sudo only for the listed Dovecot scripts.
- Keep scripts owned by root and writable only by trusted administrators.
- Do not store credentials in scripts, templates, or macros.
- Use secure macros or a vault for any future credential-based checks.
