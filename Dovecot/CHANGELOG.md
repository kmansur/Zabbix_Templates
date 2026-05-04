# Changelog

Portuguese version: [CHANGELOG.pt-BR.md](CHANGELOG.pt-BR.md)

All notable changes to this project are documented here.

Documentation maintenance: when this English changelog is updated, update
`CHANGELOG.pt-BR.md` in the same change.

## 2.0.0 - Unreleased

### Added

- Added `Template_Dovecot_7.0.yaml` for Zabbix 7.0.
- Added a JSON-based `dovecot.stats` master item design with dependent items for
  collector status, IMAP connections, POP3 connections, and total connections.
- Added service enable macros for IMAP, IMAPS, POP3, and POP3S availability
  triggers.
- Added port macros for IMAP, IMAPS, POP3, and POP3S service checks.
- Added configuration file path macros for checksum monitoring.
- Added collector health and last error items.

### Changed

- Updated `dovecot_stats.sh` to return valid JSON instead of CSV.
- Updated legacy IMAP and POP3 counter scripts with stricter protocol matching.
- Updated UserParameters to call session scripts with `sudo -n`.
- Updated English and Portuguese documentation for the 2.0.0 workflow.

### Preserved

- Kept `Template_App_Dovecot.xml` as the legacy Zabbix 5.0 template from
  version 1.0.0.
- Kept `dovecot.imap` and `dovecot.pop` UserParameters for compatibility.

## 1.0.0 - 2026-05-03

### Added

- Added English and Portuguese README files for the Dovecot template project.
- Added English and Portuguese changelog files.

### Changed

- Marked the current production Dovecot template version as `1.0.0`.
- Reorganized the Dovecot project layout so the template, scripts, and
  UserParameter configuration live in the same directory.

### Preserved

- Preserved the existing Zabbix 5.0 XML template behavior.
- Preserved the existing Dovecot session scripts.
- Preserved the existing Zabbix agent UserParameter definitions.
