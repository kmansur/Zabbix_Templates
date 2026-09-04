#!/usr/bin/env python3
"""
UniFi Dashboard Telemetry collector
Version: 0.8.0-rc2
Author: Karim Mansur / Net Tech

Companion collector for UniFi UDM Pro API Monitoring. It adds per-client
traffic/RSSI, site DPI application traffic and optional controller-local Wi-Fi
connectivity metrics used by Zabbix-UniFi-Dashboard.

Only Python standard-library modules are required.
"""

import argparse
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request

VERSION = "0.8.0-rc2"
DEFAULT_TIMEOUT = 20
LIMIT = 200


class RequestError(RuntimeError):
    def __init__(self, message, status=None, details=None):
        super().__init__(message)
        self.status = status
        self.details = details


def emit(value):
    print(json.dumps(value, separators=(",", ":"), sort_keys=True))


def root(base):
    base = (base or "").rstrip("/")
    for suffix in ("/proxy/network/integration/v1", "/proxy/network/integration"):
        if base.endswith(suffix):
            return base[:-len(suffix)]
    return base


def req(url, key, method="GET", payload=None, query=None, timeout=DEFAULT_TIMEOUT, verify=False):
    if query:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(query)
    body = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json", "X-API-KEY": key, "X-API-Key": key}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, headers=headers, data=body, method=method)
    context = None if verify else ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            raw = response.read().decode()
    except urllib.error.HTTPError as exc:
        details = exc.read().decode(errors="replace")[:500]
        raise RequestError("HTTP error", exc.code, details) from exc
    except urllib.error.URLError as exc:
        raise RequestError("connection error", details=str(exc.reason)) from exc
    except TimeoutError as exc:
        raise RequestError("request timed out") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RequestError("invalid JSON response", details=raw[:500]) from exc


def legacy(base, site, path):
    return f"{root(base)}/proxy/network/api/s/{urllib.parse.quote(site or 'default')}/{path}"


def v2(base, site, path):
    return f"{root(base)}/proxy/network/v2/api/site/{urllib.parse.quote(site or 'default')}/{path}"


def integration(base, path):
    return f"{root(base)}/proxy/network/integration/v1/{path}"


def num(value):
    try:
        return None if value in (None, "") else float(value)
    except (TypeError, ValueError):
        return None


def first(row, *keys):
    if not isinstance(row, dict):
        return None
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def safe_id(value):
    return str(value or "").strip().replace("[", "_").replace("]", "_").replace(",", "_")


def rssi_dbm(row):
    for key in ("signal", "signal_dbm", "signalDbm", "rssi"):
        value = num(row.get(key))
        if value is not None and -120 <= value <= 0:
            return round(value, 1)
    return None


def bytes_total(row):
    direct = num(first(row, "traffic_bytes", "trafficBytes", "bytes", "total_bytes", "totalBytes"))
    if direct is not None:
        return max(0, int(direct))
    rx = num(first(row, "rx_bytes", "rxBytes", "bytes_rx", "bytesRx")) or 0
    tx = num(first(row, "tx_bytes", "txBytes", "bytes_tx", "bytesTx")) or 0
    usage = row.get("traffic_usage") or row.get("trafficUsage")
    if isinstance(usage, dict):
        rx = num(first(usage, "rx_bytes", "rxBytes", "downloadBytes")) or rx
        tx = num(first(usage, "tx_bytes", "txBytes", "uploadBytes")) or tx
    return max(0, int(rx + tx))


def clients(base, key, site, timeout, verify):
    payload = req(
        legacy(base, site, "stat/sta"), key,
        query={"include_traffic_usage": "true"}, timeout=timeout, verify=verify
    )
    result, signals = {}, []
    for row in payload.get("data", []):
        if not isinstance(row, dict):
            continue
        cid = safe_id(first(row, "_id", "id", "client_id", "clientId", "mac"))
        if not cid:
            continue
        wired = first(row, "is_wired", "isWired", "wired")
        access = str(first(row, "type", "access_type", "accessType") or "").upper()
        wireless = (
            wired is False or str(wired).lower() in {"0", "false", "no"}
            or access == "WIRELESS"
            or any(row.get(k) not in (None, "") for k in ("essid", "radio", "ap_mac", "apMac"))
        )
        signal = rssi_dbm(row) if wireless else None
        if signal is not None:
            signals.append(signal)
        result[cid] = {
            "name": str(first(row, "name", "hostname", "display_name", "displayName")
                        or row.get("oui") or row.get("mac") or cid),
            "mac": str(row.get("mac") or ""),
            "ip": str(first(row, "ip", "ipAddress") or ""),
            "wireless": wireless,
            "rssi": signal,
            "traffic_bytes": bytes_total(row),
            "ap_mac": str(first(row, "ap_mac", "apMac") or ""),
            "ssid": str(first(row, "essid", "ssid") or "")
        }
    ordered = sorted(signals)
    median = None
    if ordered:
        middle = len(ordered) // 2
        median = ordered[middle] if len(ordered) % 2 else round((ordered[middle-1] + ordered[middle]) / 2, 1)
    return {
        "clients": result,
        "summary": {
            "clients": len(result),
            "wireless_with_rssi": len(signals),
            "rssi_average": round(sum(signals) / len(signals), 1) if signals else None,
            "rssi_median": median,
            "excellent": sum(v >= -60 for v in signals),
            "good": sum(-70 <= v < -60 for v in signals),
            "fair": sum(-75 <= v < -70 for v in signals),
            "poor": sum(-80 <= v < -75 for v in signals),
            "critical": sum(v < -80 for v in signals)
        }
    }


def dpi_catalog(base, key, timeout, verify):
    catalog, offset = {}, 0
    try:
        while True:
            payload = req(
                integration(base, "dpi/applications"), key,
                query={"offset": offset, "limit": LIMIT}, timeout=timeout, verify=verify
            )
            rows = payload.get("data", [])
            for row in rows:
                appid = safe_id(first(row, "id", "applicationId", "appId"))
                if appid:
                    catalog[appid] = str(first(row, "name", "displayName") or f"App {appid}")
            count = int(payload.get("count", len(rows)))
            offset += count
            if count <= 0 or offset >= int(payload.get("totalCount", offset)):
                break
    except RequestError:
        pass
    return catalog


def dpi(base, key, site, timeout, verify):
    payload = req(
        legacy(base, site, "stat/sitedpi"), key, method="POST",
        payload={"type": "by_app"}, timeout=timeout, verify=verify
    )
    catalog, apps = dpi_catalog(base, key, timeout, verify), {}
    for row in payload.get("data", []):
        if not isinstance(row, dict):
            continue
        appid = safe_id(first(row, "app", "app_id", "appId", "application_id", "applicationId", "id"))
        if not appid:
            continue
        rx = num(first(row, "rx_bytes", "rxBytes", "bytes_rx", "bytesRx")) or 0
        tx = num(first(row, "tx_bytes", "txBytes", "bytes_tx", "bytesTx")) or 0
        total = num(first(row, "bytes", "total_bytes", "totalBytes", "num_bytes", "numBytes"))
        total = rx + tx if total is None else total
        item = apps.setdefault(appid, {
            "name": str(first(row, "app_name", "appName", "name") or catalog.get(appid) or f"App {appid}"),
            "bytes": 0, "rx_bytes": 0, "tx_bytes": 0,
            "category": str(first(row, "cat_name", "categoryName", "category") or "")
        })
        item["bytes"] += max(0, int(total))
        item["rx_bytes"] += max(0, int(rx))
        item["tx_bytes"] += max(0, int(tx))
    return {"applications": apps, "summary": {"applications": len(apps), "bytes": sum(x["bytes"] for x in apps.values())}}


ALIASES = {
    "association": {"association", "association_success", "association_success_rate",
                    "association_success_pct", "associationsuccess", "associationsuccessrate",
                    "assoc_success", "assoc_success_rate", "assoc_success_pct"},
    "authentication": {"authentication", "authentication_success", "authentication_success_rate",
                       "authentication_success_pct", "authenticationsuccess",
                       "authenticationsuccessrate", "auth_success", "auth_success_rate", "auth_success_pct"},
    "dhcp": {"dhcp", "dhcp_success", "dhcp_success_rate", "dhcp_success_pct", "dhcpsuccess", "dhcpsuccessrate"},
    "dns": {"dns", "dns_success", "dns_success_rate", "dns_success_pct", "dnssuccess", "dnssuccessrate"}
}


def find_metric(payload, aliases):
    found = []
    aliases = {x.lower().replace("-", "_") for x in aliases}

    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = str(key).lower().replace("-", "_")
                if normalized in aliases:
                    candidate = num(child)
                    if candidate is not None:
                        found.append(candidate)
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(payload)
    if not found:
        return None
    value = found[0] * 100 if 0 <= found[0] <= 1 else found[0]
    return round(value, 2) if 0 <= value <= 100 else None


def wifi_performance(base, key, site, timeout, verify):
    endpoint = "v2/api/site/<site>/wifi-stats/performance"
    try:
        payload = req(v2(base, site, "wifi-stats/performance"), key, timeout=timeout, verify=verify)
    except RequestError as exc:
        return {"available": False, "endpoint": endpoint, "association": None,
                "authentication": None, "dhcp": None, "dns": None,
                "error": str(exc), "status": exc.status}
    metrics = {name: find_metric(payload, aliases) for name, aliases in ALIASES.items()}
    return {"available": any(v is not None for v in metrics.values()), "endpoint": endpoint, **metrics}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("clients", "dpi", "wifi-performance", "version"))
    parser.add_argument("base_url", nargs="?")
    parser.add_argument("api_key", nargs="?")
    parser.add_argument("site", nargs="?", default="default")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--verify-tls", action="store_true")

    # Zabbix leaves a user macro literal (for example {$UNIFI.TLS.ARG}) in the
    # command line when that macro is not defined on the host or on the template
    # that owns the item. The companion template is linked beside the base
    # template, so sibling-template macros are not guaranteed to resolve here.
    # Ignore only unresolved Zabbix macro tokens; keep rejecting all other
    # unknown arguments so real configuration mistakes remain visible.
    args, unknown = parser.parse_known_args()
    unexpected = [
        token for token in unknown
        if not (token.startswith("{$") and token.endswith("}"))
    ]
    if unexpected:
        parser.error("unrecognized arguments: " + " ".join(unexpected))

    if args.command == "version":
        emit({"version": VERSION})
        return
    if not args.base_url or not args.api_key:
        emit({"error": "missing UniFi API URL or API key"})
        return

    try:
        func = {"clients": clients, "dpi": dpi, "wifi-performance": wifi_performance}[args.command]
        emit(func(args.base_url, args.api_key, args.site, args.timeout, args.verify_tls))
    except RequestError as exc:
        emit({"error": str(exc), "status": exc.status, "details": exc.details})
    except Exception as exc:
        emit({"error": "collector failure", "details": str(exc)})


if __name__ == "__main__":
    main()
