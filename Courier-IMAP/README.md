# Courier-IMAP Zabbix Template

Portuguese version: [README.pt-BR.md](README.pt-BR.md)

> Development version: 1.1.0
>
> Documentation maintenance: when this English README is updated, update `README.pt-BR.md` in the same change.

Zabbix template project for monitoring Courier-IMAP and Courier-POP3 logins on FreeBSD through Zabbix agent UserParameters. This repository keeps the original Zabbix 3.2 XML export available in a versioned template directory and organizes scripts, agent configuration, validation notes, and changelog files using the current repository layout.

## Files

- `templates/3.2/Template_Courier_IMAP_3.2.xml`: legacy Zabbix 3.2 XML template export.
- `scripts/courier_imapd.sh`: counts IMAP login events from the previous minute.
- `scripts/courier_imapd-ssl.sh`: counts IMAPS login events from the previous minute.
- `scripts/courier_pop3d.sh`: counts POP3 login events from the previous minute.
- `scripts/courier_pop3d-ssl.sh`: counts POP3S login events from the previous minute.
- `agent/userparameter_courier.conf`: Zabbix agent UserParameter definitions.
- `docs/VALIDATION.md`: validation and pre-production checklist.
- `CHANGELOG.md`: English changelog.
- `CHANGELOG.pt-BR.md`: Portuguese changelog.

## Monitored Data

- IMAP login events per minute.
- IMAPS login events per minute.
- POP3 login events per minute.
- POP3S login events per minute.
- Courier-IMAP maximum active connection log events.
- Courier-IMAP maximum connection limit per IP log events.
- Checksum changes for selected Courier-IMAP and maildrop configuration files.

## Requirements

- Zabbix server compatible with template export version 3.2.
- Zabbix agent installed on the Courier-IMAP host.
- FreeBSD host with Courier-IMAP/Courier-POP3 logging to `/var/log/maillog`.
- Zabbix agent user with read access to `/var/log/maillog`.
- POSIX shell and FreeBSD `date` with `-j -v-1M` support.

Default paths used by this version:

```text
/usr/local/scripts/
/usr/local/etc/courier-imap/
/usr/local/etc/maildroprc
/var/log/maillog
```

The scripts support `COURIER_MAILLOG` as an environment override for the mail log path. Environment overrides might not be preserved by the service manager or by restricted agent execution policies.

## Installation

1. Copy the scripts from `scripts/` to `/usr/local/scripts/` and set mode `755`.
2. Restrict ownership:

   ```bash
   chown root:wheel /usr/local/scripts/courier_imapd.sh
   chown root:wheel /usr/local/scripts/courier_imapd-ssl.sh
   chown root:wheel /usr/local/scripts/courier_pop3d.sh
   chown root:wheel /usr/local/scripts/courier_pop3d-ssl.sh
   ```

3. Copy `agent/userparameter_courier.conf` to the Zabbix agent include directory.
4. Make sure the Zabbix agent can read `/var/log/maillog`.
5. Restart the Zabbix agent.
6. Import `templates/3.2/Template_Courier_IMAP_3.2.xml` into Zabbix.
7. Link `Template App MAIL Courier-IMAP` to the Courier-IMAP host.

## Validation

```bash
sh -n /usr/local/scripts/courier_imapd.sh
sh -n /usr/local/scripts/courier_imapd-ssl.sh
sh -n /usr/local/scripts/courier_pop3d.sh
sh -n /usr/local/scripts/courier_pop3d-ssl.sh
sudo -u zabbix zabbix_agentd -t imapd
sudo -u zabbix zabbix_agentd -t imapd-ssl
sudo -u zabbix zabbix_agentd -t pop3d
sudo -u zabbix zabbix_agentd -t pop3d-ssl
```

More checks are available in `docs/VALIDATION.md`.

## Counting Method

The four scripts count `LOGIN` records in `/var/log/maillog` that match the previous minute and the Courier service name. The plain IMAP and POP3 scripts exclude their SSL variants so TLS logins are not double-counted.

## Compatibility Notes

- `templates/3.2/Template_Courier_IMAP_3.2.xml` is the preserved legacy export for this project.
- The item keys remain `imapd`, `imapd-ssl`, `pop3d`, and `pop3d-ssl` to avoid breaking existing hosts.
- Log trigger checks still use `/var/log/maillog` directly in the Zabbix template.
- The scripts are FreeBSD-oriented because they depend on FreeBSD `date` syntax. Validate before adapting them to Linux.
