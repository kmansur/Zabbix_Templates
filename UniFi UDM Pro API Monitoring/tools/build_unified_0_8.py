#!/usr/bin/env python3
"""Build the UniFi 0.8 unified collector and flattened Zabbix templates.

The validated 0.7 collector and 0.8 dashboard telemetry collector remain as
readable source modules during the release-candidate phase. This build step
produces one deployable external script and one importable template per Zabbix
major version without duplicating their source by hand.
"""

from __future__ import annotations

import argparse
import pathlib
import textwrap
import uuid

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"
VERSION = "0.8.0-rc5"
VENDOR_VERSION = "0.8-0-rc5"
SCRIPT_NAME = "unifi_udm_pro_api.py"

PERIODS = {
    "1h": {"seconds": 3600, "delay": "5m"},
    "1d": {"seconds": 86400, "delay": "5m"},
    "1w": {"seconds": 604800, "delay": "1h"},
    "1m": {"seconds": 2592000, "delay": "6h"},
}


def stable_uuid(seed: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, f"https://nettech.com.br/zabbix/unifi/0.8/{seed}").hex


def qkey(command: str, *args: str) -> str:
    quoted = [f'"{command}"'] + [f'"{value}"' for value in args]
    return f"{SCRIPT_NAME}[{','.join(quoted)}]"


def traffic_key(seconds: int) -> str:
    return qkey(
        "dashboard-traffic",
        "{$UNIFI.API.URL}",
        "{$UNIFI.API.KEY}",
        "{$UNIFI.NETWORK.SITE}",
        str(seconds),
        "{$UNIFI.TLS.ARG}",
    )


def status_key() -> str:
    return qkey(
        "dashboard-client-status",
        "{$UNIFI.API.URL}",
        "{$UNIFI.API.KEY}",
        "{$UNIFI.NETWORK.SITE}",
        "{$UNIFI.TLS.ARG}",
    )


def wifi_key() -> str:
    return qkey(
        "wifi-connectivity",
        "{$UNIFI.API.URL}",
        "{$UNIFI.API.KEY}",
        "{$UNIFI.NETWORK.SITE}",
        "{$UNIFI.TLS.ARG}",
    )


def catalog_key() -> str:
    return qkey(
        "dpi-catalog",
        "{$UNIFI.API.URL}",
        "{$UNIFI.API.KEY}",
        "{$UNIFI.NETWORK.SITE}",
        "{$UNIFI.TLS.ARG}",
    )


def external_item(seed: str, name: str, key: str, delay: str, component: str) -> dict:
    return {
        "uuid": stable_uuid(seed),
        "name": name,
        "type": "EXTERNAL",
        "key": key,
        "delay": delay,
        "history": "1d",
        "value_type": "TEXT",
        "trends": "0",
        "timeout": "60s",
        "tags": [
            {"tag": "component", "value": "dashboard-telemetry"},
            {"tag": "component", "value": component},
        ],
    }


def dependent_item(seed: str, name: str, key: str, master: str, js: str, *, value_type=None, units=None, history="90d") -> dict:
    item = {
        "uuid": stable_uuid(seed),
        "name": name,
        "type": "DEPENDENT",
        "key": key,
        "delay": "0",
        "history": history,
        "preprocessing": [{"type": "JAVASCRIPT", "parameters": [js]}],
        "master_item": {"key": master},
        "tags": [{"tag": "component", "value": "dashboard-telemetry"}],
    }
    if value_type:
        item["value_type"] = value_type
        if value_type in {"CHAR", "TEXT"}:
            item["trends"] = "0"
    if units:
        item["units"] = units
    return item


def prototype(seed: str, name: str, key: str, master: str, js: str, *, value_type=None, units=None, history="30d") -> dict:
    item = dependent_item(seed, name, key, master, js, value_type=value_type, units=units, history=history)
    item["tags"] = [{"tag": "component", "value": "dashboard-telemetry"}]
    return item


def dashboard_extension() -> tuple[list[dict], list[dict]]:
    items: list[dict] = []
    rules: list[dict] = []

    traffic_masters = {}
    for period, meta in PERIODS.items():
        key = traffic_key(meta["seconds"])
        traffic_masters[period] = key
        items.append(external_item(
            f"traffic-master-{period}",
            f"UniFi dashboard traffic {period} raw",
            key,
            meta["delay"],
            "traffic",
        ))

    current_status = status_key()
    items.append(external_item(
        "client-status-master",
        "UniFi dashboard current client status raw",
        current_status,
        "2m",
        "clients",
    ))

    catalog = catalog_key()
    items.append(external_item(
        "dpi-catalog-master",
        "UniFi DPI application catalog raw",
        catalog,
        "12h",
        "dpi",
    ))

    wifi = wifi_key()
    items.append(external_item(
        "wifi-connectivity-master",
        "UniFi Wi-Fi connectivity raw",
        wifi,
        "2m",
        "wifi",
    ))

    for metric, json_name, label in [
        ("association", "association", "association"),
        ("authentication", "authentication", "authentication"),
        ("dhcp", "dhcp", "DHCP"),
        ("dns", "dns", "DNS"),
    ]:
        items.append(dependent_item(
            f"wifi-{metric}",
            f"UniFi Wi-Fi {label} success",
            f"unifi.wifi.{metric}.success",
            wifi,
            f'try {{ var d=JSON.parse(value), v=d.{json_name}; return (v === null || typeof v === "undefined") ? "" : v; }} catch (e) {{ return ""; }}',
            value_type="CHAR",
        ))

    month_master = traffic_masters["1m"]
    client_prototypes = [
        prototype(
            "client-name",
            "UniFi client {#UNIFI.CLIENT.NAME} name",
            "unifi.client.name[{#UNIFI.CLIENT.ID}]",
            month_master,
            'var d=JSON.parse(value), c=(d.clients||{})["{#UNIFI.CLIENT.ID}"]||{}; return c.name || "{#UNIFI.CLIENT.ID}";',
            value_type="CHAR",
        )
    ]

    for period in PERIODS:
        client_prototypes.append(prototype(
            f"client-traffic-{period}",
            f"UniFi client {{#UNIFI.CLIENT.NAME}} traffic {period}",
            f"unifi.client.traffic.bytes[{period},{{#UNIFI.CLIENT.ID}}]",
            traffic_masters[period],
            'var d=JSON.parse(value), c=(d.clients||{})["{#UNIFI.CLIENT.ID}"]||{}; return c.traffic_bytes || 0;',
            units="B",
        ))

    # Compatibility key for dashboard 0.1 / existing 24-hour consumers.
    client_prototypes.append(prototype(
        "client-traffic-legacy-1d",
        "UniFi client {#UNIFI.CLIENT.NAME} traffic",
        "unifi.client.traffic.bytes[{#UNIFI.CLIENT.ID}]",
        traffic_masters["1d"],
        'var d=JSON.parse(value), c=(d.clients||{})["{#UNIFI.CLIENT.ID}"]||{}; return c.traffic_bytes || 0;',
        units="B",
    ))

    rules.append({
        "uuid": stable_uuid("client-traffic-discovery"),
        "name": "UniFi dashboard client traffic discovery",
        "type": "DEPENDENT",
        "key": "unifi.dashboard.clients.traffic.discovery",
        "lifetime": "30d",
        "item_prototypes": client_prototypes,
        "master_item": {"key": month_master},
        "preprocessing": [{
            "type": "JAVASCRIPT",
            "parameters": [textwrap.dedent("""\
                var d=JSON.parse(value), out=[], clients=d.clients||{};
                Object.keys(clients).forEach(function(id) {
                  var c=clients[id]||{};
                  out.push({"{#UNIFI.CLIENT.ID}":id,"{#UNIFI.CLIENT.NAME}":c.name||id});
                });
                return JSON.stringify(out);
            """).rstrip()],
        }],
    })

    rules.append({
        "uuid": stable_uuid("client-rssi-discovery"),
        "name": "UniFi dashboard current wireless RSSI discovery",
        "type": "DEPENDENT",
        "key": "unifi.dashboard.clients.rssi.discovery",
        "lifetime": "7d",
        "item_prototypes": [prototype(
            "client-rssi",
            "UniFi wireless client {#UNIFI.CLIENT.NAME} RSSI",
            "unifi.radio.rssi[{#UNIFI.CLIENT.ID}]",
            current_status,
            'var d=JSON.parse(value), c=(d.clients||{})["{#UNIFI.CLIENT.ID}"]||{}; return c.rssi;',
            value_type="FLOAT",
            units="dBm",
        )],
        "master_item": {"key": current_status},
        "preprocessing": [{
            "type": "JAVASCRIPT",
            "parameters": [textwrap.dedent("""\
                var d=JSON.parse(value), out=[], clients=d.clients||{};
                Object.keys(clients).forEach(function(id) {
                  var c=clients[id]||{};
                  if (c.rssi !== null && typeof c.rssi !== "undefined") {
                    out.push({"{#UNIFI.CLIENT.ID}":id,"{#UNIFI.CLIENT.NAME}":c.name||id});
                  }
                });
                return JSON.stringify(out);
            """).rstrip()],
        }],
    })

    app_prototypes = [prototype(
        "dpi-name",
        "UniFi DPI application {#UNIFI.DPI.APP.NAME} name",
        "unifi.dpi.app.name[{#UNIFI.DPI.APP.ID}]",
        catalog,
        'var d=JSON.parse(value), apps=d.applications||{}; return apps["{#UNIFI.DPI.APP.ID}"] || "{#UNIFI.DPI.APP.NAME}";',
        value_type="CHAR",
    )]

    for period in PERIODS:
        app_prototypes.append(prototype(
            f"dpi-traffic-{period}",
            f"UniFi DPI application {{#UNIFI.DPI.APP.NAME}} traffic {period}",
            f"unifi.dpi.app.bytes[{period},{{#UNIFI.DPI.APP.ID}}]",
            traffic_masters[period],
            'var d=JSON.parse(value), a=(d.applications||{})["{#UNIFI.DPI.APP.ID}"]||{}; return a.bytes || 0;',
            units="B",
        ))

    app_prototypes.append(prototype(
        "dpi-traffic-legacy-1d",
        "UniFi DPI application {#UNIFI.DPI.APP.NAME} traffic",
        "unifi.dpi.app.bytes[{#UNIFI.DPI.APP.ID}]",
        traffic_masters["1d"],
        'var d=JSON.parse(value), a=(d.applications||{})["{#UNIFI.DPI.APP.ID}"]||{}; return a.bytes || 0;',
        units="B",
    ))

    rules.append({
        "uuid": stable_uuid("dpi-discovery"),
        "name": "UniFi dashboard DPI application discovery",
        "type": "DEPENDENT",
        "key": "unifi.dashboard.dpi.app.discovery",
        "lifetime": "90d",
        "item_prototypes": app_prototypes,
        "master_item": {"key": month_master},
        "preprocessing": [{
            "type": "JAVASCRIPT",
            "parameters": [textwrap.dedent("""\
                var d=JSON.parse(value), out=[], apps=d.applications||{};
                Object.keys(apps).forEach(function(id) {
                  var a=apps[id]||{};
                  out.push({"{#UNIFI.DPI.APP.ID}":id,"{#UNIFI.DPI.APP.NAME}":a.name||("App "+id)});
                });
                return JSON.stringify(out);
            """).rstrip()],
        }],
    })

    return items, rules


def build_script(core_source: str, dashboard_source: str) -> str:
    return textwrap.dedent(f'''\
        #!/usr/bin/env python3
        """Generated UniFi unified collector {VERSION}.

        Source modules are embedded from unifi_udm_pro_api.py and
        unifi_dashboard_telemetry.py. Do not edit this generated file directly.
        """
        import argparse
        import json
        import sys

        VERSION = {VERSION!r}
        CORE_SOURCE = {core_source!r}
        DASHBOARD_SOURCE = {dashboard_source!r}

        def load_namespace(source, name):
            namespace = {{"__name__": name, "__file__": __file__}}
            exec(compile(source, __file__, "exec"), namespace)
            return namespace

        def emit(value):
            print(json.dumps(value, separators=(",", ":"), sort_keys=True))

        def common_args():
            parser = argparse.ArgumentParser(add_help=False)
            parser.add_argument("command")
            parser.add_argument("base_url", nargs="?")
            parser.add_argument("api_key", nargs="?")
            parser.add_argument("site", nargs="?", default="default")
            parser.add_argument("window", nargs="?")
            parser.add_argument("--timeout", type=int, default=20)
            parser.add_argument("--verify-tls", action="store_true")
            args, unknown = parser.parse_known_args()
            unknown = [x for x in unknown if not (x.startswith("{{$") and x.endswith("}}"))]
            if unknown:
                parser.error("unrecognized arguments: " + " ".join(unknown))
            if args.window and args.window.startswith("{{$") and args.window.endswith("}}"):
                args.window = None
            return args

        def dashboard_traffic(ns, args):
            if not args.base_url or not args.api_key:
                return {{"error": "missing UniFi API URL or API key"}}
            try:
                window = max(60, int(args.window or 86400))
            except ValueError:
                return {{"error": "invalid traffic window", "window": args.window}}

            verify = args.verify_tls
            rows = []
            try:
                rows = ns["legacy_station_rows"](args.base_url, args.api_key, args.site, args.timeout, verify)
            except ns["RequestError"]:
                pass

            clients = {{}}
            station_by_mac = {{}}
            for row in rows:
                cid, station = ns["normalized_station"](row, traffic_bytes=0)
                if not cid or not station:
                    continue
                clients[cid] = station
                mac = str(station.get("mac") or "").lower()
                if mac:
                    station_by_mac[mac] = cid

            payload, start, end = ns["traffic_snapshot"](
                args.base_url, args.api_key, args.site, args.timeout, verify, window
            )

            for entry in payload.get("client_usage_by_app", []):
                if not isinstance(entry, dict):
                    continue
                client = entry.get("client") or {{}}
                mac = str(ns["first"](client, "mac", "macAddress") or "")
                cid = station_by_mac.get(mac.lower()) or ns["safe_id"](
                    mac or ns["first"](client, "id", "client_id", "clientId", "name", "hostname")
                )
                if not cid:
                    continue
                usage = entry.get("usage_by_app") or []
                total = sum(ns["bytes_total"](row) for row in usage if isinstance(row, dict))
                wired = ns["first"](client, "is_wired", "isWired", "wired")
                wireless = wired is False or str(wired).lower() in {{"0", "false", "no"}}
                if cid in clients:
                    clients[cid]["traffic_bytes"] = max(0, int(total))
                    name = ns["first"](client, "name", "hostname", "display_name", "displayName")
                    if name:
                        clients[cid]["name"] = str(name)
                    clients[cid]["wireless"] = wireless
                else:
                    clients[cid] = {{
                        "name": str(ns["first"](client, "name", "hostname", "display_name", "displayName") or mac or cid),
                        "mac": mac,
                        "ip": str(ns["first"](client, "ip", "ipAddress") or ""),
                        "wireless": wireless,
                        "rssi": None,
                        "traffic_bytes": max(0, int(total)),
                        "ap_mac": "",
                        "ssid": ""
                    }}

            applications = {{}}
            for row in payload.get("total_usage_by_app", []):
                if not isinstance(row, dict):
                    continue
                category = ns["first"](row, "category", "category_id", "categoryId")
                application = ns["first"](row, "application", "app", "application_id", "applicationId", "appId")
                compound = ns["compound_dpi_id"](category, application)
                if compound is None:
                    continue
                appid = ns["safe_id"](compound)
                rx = ns["num"](ns["first"](row, "bytes_received", "rx_bytes", "rxBytes", "bytes_rx", "bytesRx")) or 0
                tx = ns["num"](ns["first"](row, "bytes_transmitted", "tx_bytes", "txBytes", "bytes_tx", "bytesTx")) or 0
                total = ns["num"](ns["first"](row, "total_bytes", "totalBytes", "bytes", "num_bytes", "numBytes"))
                total = rx + tx if total is None else total
                applications[appid] = {{
                    "name": "Unknown" if int(category) == 255 or int(application) == 65535 else f"App {{category}}/{{application}}",
                    "bytes": max(0, int(total)),
                    "rx_bytes": max(0, int(rx)),
                    "tx_bytes": max(0, int(tx)),
                    "category": str(category),
                    "application": str(application),
                    "client_count": int(ns["num"](row.get("client_count")) or 0)
                }}

            return {{
                "clients": clients,
                "applications": applications,
                "summary": {{
                    "window_seconds": window,
                    "start": start,
                    "end": end,
                    "clients": len(clients),
                    "applications": len(applications),
                    "bytes": sum(app["bytes"] for app in applications.values()),
                    "traffic_source": "v2/traffic"
                }}
            }}

        def client_status(ns, args):
            rows = ns["legacy_station_rows"](
                args.base_url, args.api_key, args.site, args.timeout, args.verify_tls
            )
            clients = {{}}
            for row in rows:
                cid, station = ns["normalized_station"](row, traffic_bytes=0)
                if cid and station:
                    clients[cid] = station
            return {{"clients": clients, "summary": {{"clients": len(clients), "source": "legacy/stat/sta"}}}}

        def dpi_catalog(ns, args):
            catalog = ns["dpi_catalog"](
                args.base_url, args.api_key, args.timeout, args.verify_tls
            )
            return {{"applications": catalog, "summary": {{"applications": len(catalog)}}}}

        def main():
            command = sys.argv[1] if len(sys.argv) > 1 else ""
            if command == "version":
                emit({{"version": VERSION, "unified": True}})
                return

            unified_commands = {{"dashboard-traffic", "dashboard-client-status", "dpi-catalog", "wifi-connectivity"}}
            if command in unified_commands:
                args = common_args()
                ns = load_namespace(DASHBOARD_SOURCE, "_unifi_dashboard_embedded")
                try:
                    if command == "dashboard-traffic":
                        emit(dashboard_traffic(ns, args))
                    elif command == "dashboard-client-status":
                        emit(client_status(ns, args))
                    elif command == "dpi-catalog":
                        emit(dpi_catalog(ns, args))
                    else:
                        emit(ns["wifi_performance"](
                            args.base_url, args.api_key, args.site,
                            args.timeout, args.verify_tls, 0
                        ))
                except ns["RequestError"] as exc:
                    emit({{"error": str(exc), "status": exc.status, "details": exc.details}})
                except Exception as exc:
                    emit({{"error": "collector failure", "details": str(exc)}})
                return

            if command in {{"clients", "dpi", "wifi-performance"}}:
                ns = load_namespace(DASHBOARD_SOURCE, "_unifi_dashboard_embedded")
                ns["main"]()
                return

            ns = load_namespace(CORE_SOURCE, "_unifi_core_embedded")
            ns["main"]()

        if __name__ == "__main__":
            main()
    ''')


def build_template(version: str, base_path: pathlib.Path) -> dict:
    with base_path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)

    export = document["zabbix_export"]
    template = export["templates"][0]
    template["description"] = (
        f"UniFi UDM Pro API Monitoring {VERSION}. Unified collector/template release candidate. "
        "Adds dashboard telemetry, rolling 1h/1d/1w/30d traffic windows, current client RSSI, "
        "DPI application ranking and Wi-Fi connectivity while retaining the existing 0.7 API contracts."
    )
    template.setdefault("vendor", {})["name"] = "Net Tech"
    template["vendor"]["version"] = VENDOR_VERSION

    items, rules = dashboard_extension()
    template.setdefault("items", []).extend(items)
    template.setdefault("discovery_rules", []).extend(rules)
    return document


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Build and validate outputs without changing source files.")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    core = (ROOT / "unifi_udm_pro_api.py").read_text(encoding="utf-8")
    dashboard = (ROOT / "unifi_dashboard_telemetry.py").read_text(encoding="utf-8")

    unified_script = build_script(core, dashboard)
    script_path = OUT / "unifi_udm_pro_api.py"
    script_path.write_text(unified_script, encoding="utf-8")
    script_path.chmod(0o755)
    compile(unified_script, str(script_path), "exec")

    for version in ("7.0", "8.0"):
        source = ROOT / version / f"UniFi_UDM_Pro_API_Monitoring_{version}.yaml"
        output = OUT / f"UniFi_UDM_Pro_API_Monitoring_Unified_{version}.yaml"
        document = build_template(version, source)
        output.write_text(
            yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=120),
            encoding="utf-8",
        )

    print(f"Built unified collector/template {VERSION} in {OUT}")
    if args.check:
        print("Validation: Python syntax and YAML parsing passed")


if __name__ == "__main__":
    main()
