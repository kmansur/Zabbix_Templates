#!/usr/bin/env python3
"""Create side-by-side staging copies of the generated unified 0.8 templates.

The staging templates use a different template name/UUID and an isolated
external-script filename so they can be imported and exercised without
updating either the production template or production collector. Link a
staging template only to a cloned Zabbix host during RC validation.
"""

from __future__ import annotations

import pathlib
import uuid

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
PRODUCTION_NAME = "UniFi UDM Pro API Monitoring"
STAGING_NAME = "UniFi UDM Pro API Monitoring Unified RC"
PRODUCTION_SCRIPT = "unifi_udm_pro_api.py["
STAGING_SCRIPT = "unifi_udm_pro_api_unified.py["


def replace_strings(value):
    if isinstance(value, dict):
        return {key: replace_strings(child) for key, child in value.items()}
    if isinstance(value, list):
        return [replace_strings(child) for child in value]
    if isinstance(value, str):
        return (
            value
            .replace(f"/{PRODUCTION_NAME}/", f"/{STAGING_NAME}/")
            .replace(PRODUCTION_SCRIPT, STAGING_SCRIPT)
        )
    return value


def main() -> None:
    for version in ("7.0", "8.0"):
        source = GENERATED / f"UniFi_UDM_Pro_API_Monitoring_Unified_{version}.yaml"
        target = GENERATED / f"UniFi_UDM_Pro_API_Monitoring_Unified_Staging_{version}.yaml"

        document = yaml.safe_load(source.read_text(encoding="utf-8"))
        document = replace_strings(document)
        template = document["zabbix_export"]["templates"][0]
        template["uuid"] = uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"https://nettech.com.br/zabbix/unifi/0.8/staging/{version}",
        ).hex
        template["template"] = STAGING_NAME
        template["name"] = STAGING_NAME
        template["description"] = (
            str(template.get("description", ""))
            + " STAGING COPY: use only on a cloned host for release-candidate validation."
        )

        target.write_text(
            yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=120),
            encoding="utf-8",
        )
        print(f"Built {target}")


if __name__ == "__main__":
    main()
