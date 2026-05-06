# Changelog

## 1.1.0 - 2026-05-06

- Reorganized the project into current repository directories: `templates/3.2`, `scripts`, `agent`, and `docs`.
- Moved the legacy Zabbix 3.2 XML export to `templates/3.2/Template_Courier_IMAP_3.2.xml`.
- Moved Courier collection scripts to `scripts/` and UserParameters to `agent/`.
- Updated UserParameters to use `/usr/local/scripts/`.
- Added English and Portuguese README files.
- Added validation documentation.
- Fixed minor legacy XML text issues in graph names, trigger descriptions, and displayed configuration paths.
- Avoided double-counting SSL logins in the plain IMAP and POP3 scripts.

## 1.0.0 - 2017-04-26

- Initial Courier-IMAP Zabbix 3.2 XML template export.
