# Changelog

Portuguese version: [CHANGELOG.pt-BR.md](CHANGELOG.pt-BR.md)

All notable changes to this project are documented here.

Documentation maintenance: when this English changelog is updated, update `CHANGELOG.pt-BR.md` in the same change.

## 2.0.0 - Unreleased

### Added

- Added `Template_Dovecot_7.0.yaml` for Zabbix 7.0.
- Added JSON-based `dovecot.stats` master item with dependent items.
- Added service enable macros and port macros for IMAP, IMAPS, POP3, and POP3S.
- Added recovery macros for IMAP and POP3 connection threshold triggers.
- Added `proc.num[{$DOVECOT.PROCESS.NAME}]` monitoring for the Dovecot master process.
- Added configuration file path macros for checksum monitoring.
- Added collector health and last error items.
- Added no-data trigger for the `dovecot.stats` master item.
- Added total connection warning and high triggers with recovery macros.
- Added TCP service response-time items and warning trigger for IMAP, IMAPS, POP3, and POP3S.
- Added service state value map.
- Added `Dovecot connections` and `Dovecot service response time` graphs.
- Added validation documentation and local parser tests.
- Added contribution, security, and license files.
- Added versioned template directories for Zabbix 6.0, 7.0, and 8.0.

### Changed

- Updated `dovecot_stats.sh` to use `doveadm who -1` and return valid JSON.
- Updated legacy IMAP and POP3 counter scripts to use `doveadm who -1` with stricter protocol-token matching.
- Updated service availability triggers to require a full 3-minute failure window.
- Updated connection triggers to use recovery expressions and recovery macros.
- Updated trigger names to start with `PROBLEM`, `WARNING`, or `INFO`.
- Updated UserParameters to call session scripts with `sudo -n`.
- Moved the Zabbix 5.0 XML template, legacy IMAP/POP3 counters, and legacy UserParameter file to `legacy/zabbix-5.0/`.
- Moved the current Zabbix 7.0 YAML template to `templates/7.0/Template_Dovecot_7.0.yaml`.
- Reduced the main `userparameter_dovecot.conf` to the Zabbix 7.0 keys used by the current template.
- Updated English and Portuguese documentation for the 2.0.0 workflow.

### Preserved

- Kept `legacy/zabbix-5.0/Template_App_Dovecot.xml` as the legacy Zabbix 5.0 template from version 1.0.0.
- Kept legacy `dovecot.imap` and `dovecot.pop` UserParameters in `legacy/zabbix-5.0/userparameter_dovecot_legacy.conf`.

## 1.0.0 - 2026-05-03

### Added

- Added English and Portuguese README files for the Dovecot template project.
- Added English and Portuguese changelog files.

### Changed

- Marked the current production Dovecot template version as `1.0.0`.
- Reorganized the Dovecot project layout so the template, scripts, and UserParameter configuration live in the same directory.

### Preserved

- Preserved the existing Zabbix 5.0 XML template behavior.
- Preserved the existing Dovecot session scripts.
- Preserved the existing Zabbix agent UserParameter definitions.
