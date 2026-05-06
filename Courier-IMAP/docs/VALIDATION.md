# Courier-IMAP Validation Checklist

Use this checklist before importing the template or linking it to a production host.

## Static Checks

```bash
sh -n scripts/courier_imapd.sh
sh -n scripts/courier_imapd-ssl.sh
sh -n scripts/courier_pop3d.sh
sh -n scripts/courier_pop3d-ssl.sh
```

Confirm that the XML export is well formed:

```bash
xmllint --noout templates/3.2/Template_Courier_IMAP_3.2.xml
```

## Host Checks

1. Confirm that Courier writes login events to `/var/log/maillog`.
2. Confirm that the Zabbix agent user can read `/var/log/maillog`.
3. Confirm that scripts are installed in `/usr/local/scripts/` with mode `755`.
4. Confirm that `agent/userparameter_courier.conf` is included by the Zabbix agent.
5. Restart the Zabbix agent after copying the UserParameter file.

## Agent Tests

```bash
sudo -u zabbix zabbix_agentd -t imapd
sudo -u zabbix zabbix_agentd -t imapd-ssl
sudo -u zabbix zabbix_agentd -t pop3d
sudo -u zabbix zabbix_agentd -t pop3d-ssl
```

Each key should return an unsigned integer. During quiet periods, `0` is valid.

## Import Checks

1. Import `templates/3.2/Template_Courier_IMAP_3.2.xml`.
2. Link `Template App MAIL Courier-IMAP` to a test host first.
3. Verify that all four UserParameter items become supported.
4. Verify graph rendering for IMAP and POP3 connection counters.
5. Review checksum triggers for the paths used by your Courier-IMAP installation.
