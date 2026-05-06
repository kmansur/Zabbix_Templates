# Changelog

## 1.2.0 - 2026-05-06

- Added the Zabbix 7.0 YAML export as `templates/7.0/Template_Courier_IMAP_7.0.yaml`.
- Added Zabbix 7.0 template documentation.
- Updated README and validation docs to treat the Zabbix 7.0 export as the current template.
- Kept the Zabbix 3.2 XML export documented as legacy.
- Documented the project as maintenance-only and no longer under active development.

## 1.1.0 - 2026-05-06

- Reorganized the project into current repository directories: `templates/3.2`, `scripts`, `agent`, and `docs`.
- Moved the legacy Zabbix 3.2 XML export to `templates/3.2/Template_Courier_IMAP_3.2.xml`.
- Moved Courier collection scripts to `scripts/` and UserParameters to `agent/`.
- Updated UserParameters to use `/usr/local/scripts/`.
- Added English and Portuguese README files.
- Added the MIT license.
- Added validation documentation.
- Fixed minor legacy XML text issues in graph names, trigger descriptions, and displayed configuration paths.
- Avoided double-counting SSL logins in the plain IMAP and POP3 scripts.

## 1.0.0 - 2017-04-26

- Initial Courier-IMAP Zabbix 3.2 XML template export.
