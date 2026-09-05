#!/usr/bin/env python3
"""Create side-by-side staging copies of the generated unified 0.8 templates.

The staging templates use a different template name, isolated object UUIDs and
an isolated external-script filename so they can be imported and exercised
without updating either the production template or production collector. Link
a staging template only to a cloned Zabbix host during RC validation.
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


def remap_template_uuids(value, version: str):
    """Give every template-owned object a deterministic staging UUID.

    Zabbix template imports identify template objects by UUID. Reusing item,
    trigger, discovery-rule or prototype UUIDs from the production template can
    make a side-by-side staging import collide with already imported objects.
    Only the template subtree is remapped; the template-group UUID is preserved
    so the staging template stays in the existing group.
    """
    if isinstance(value, dict):
        remapped = {}
        for key, child in value.items():
            if key == "uuid" and isinstance(child, str) and child:
                remapped[key] = uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"https://nettech.com.br/zabbix/unifi/0.8/staging/{version}/object/{child}",
                ).hex
            else:
                remapped[key] = remap_template_uuids(child, version)
        return remapped
    if isinstance(value, list):
        return [remap_template_uuids(child, version) for child in value]
    return value


def main() -> None:
    for version in ("7.0", "8.0"):
        source = GENERATED / f"UniFi_UDM_Pro_API_Monitoring_Unified_{version}.yaml"
        target = GENERATED / f"UniFi_UDM_Pro_API_Monitoring_Unified_Staging_{version}.yaml"

        document = yaml.safe_load(source.read_text(encoding="utf-8"))
        document = replace_strings(document)
        template = document["zabbix_export"]["templates"][0]
        template = remap_template_uuids(template, version)
        document["zabbix_export"]["templates"][0] = template

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
