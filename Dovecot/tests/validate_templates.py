#!/usr/bin/env python3
"""Static validation for the Dovecot Zabbix template exports."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = {
    "7.0": ROOT / "templates" / "7.0" / "Template_Dovecot_7.0.yaml",
    "8.0": ROOT / "templates" / "8.0" / "Template_Dovecot_8.0.yaml",
}

EXPECTED_KEYS = {
    "dovecot.stats",
    "dovecot.collector.available",
    "dovecot.collector.error",
    "dovecot.collector.version",
    "dovecot.connections.imap",
    "dovecot.connections.pop3",
    "dovecot.connections.total",
    "dovecot.connections.users",
    "dovecot.connections.max_per_user",
    "dovecot.version",
    "proc.num[{$DOVECOT.PROCESS.NAME}]",
    "net.tcp.service[imap,,{$DOVECOT.IMAP.PORT}]",
    "net.tcp.service[tcp,,{$DOVECOT.IMAPS.PORT}]",
    "net.tcp.service[pop,,{$DOVECOT.POP3.PORT}]",
    "net.tcp.service[tcp,,{$DOVECOT.POP3S.PORT}]",
    "net.tcp.service.perf[imap,,{$DOVECOT.IMAP.PORT}]",
    "net.tcp.service.perf[tcp,,{$DOVECOT.IMAPS.PORT}]",
    "net.tcp.service.perf[pop,,{$DOVECOT.POP3.PORT}]",
    "net.tcp.service.perf[tcp,,{$DOVECOT.POP3S.PORT}]",
    "vfs.file.cksum[{$DOVECOT.CONF.FILE}]",
    "vfs.file.cksum[{$DOVECOT.SQL.CONF.FILE}]",
}


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def validate(path: Path, export_version: str) -> None:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    assert data["zabbix_export"]["version"] == export_version, (
        f"{path}: export version mismatch"
    )

    templates = data["zabbix_export"].get("templates", [])
    assert len(templates) == 1, f"{path}: expected exactly one template"
    template = templates[0]

    vendor = template.get("vendor", {})
    assert str(vendor.get("version")) == "3.0.0", f"{path}: vendor version is not 3.0.0"

    keys = {
        obj["key"]
        for obj in walk(template)
        if isinstance(obj, dict) and isinstance(obj.get("key"), str)
    }
    missing_keys = EXPECTED_KEYS - keys
    assert not missing_keys, f"{path}: missing keys: {sorted(missing_keys)}"

    uuids = [
        obj["uuid"]
        for obj in walk(data)
        if isinstance(obj, dict) and isinstance(obj.get("uuid"), str)
    ]
    duplicates = sorted({uuid for uuid in uuids if uuids.count(uuid) > 1})
    assert not duplicates, f"{path}: duplicate UUIDs: {duplicates}"

    defined_macros = {
        macro["macro"]
        for macro in template.get("macros", [])
        if isinstance(macro, dict) and "macro" in macro
    }
    referenced_macros = set(re.findall(r"\{\$[A-Z0-9_.]+\}", text))
    missing_macros = referenced_macros - defined_macros
    assert not missing_macros, f"{path}: undefined macros: {sorted(missing_macros)}"

    assert "net.tcp.service[tcp,,{$DOVECOT.IMAP.PORT}]" not in text, (
        f"{path}: IMAP must use protocol-aware service check"
    )
    assert "net.tcp.service[tcp,,{$DOVECOT.POP3.PORT}]" not in text, (
        f"{path}: POP3 must use protocol-aware service check"
    )


def main() -> int:
    for version, path in TEMPLATES.items():
        validate(path, version)
        print(f"OK: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
