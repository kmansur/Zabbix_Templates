#!/usr/bin/env python3
"""
UniFi Dashboard Telemetry collector
Version: 0.8.0-rc4
Author: Karim Mansur / Net Tech

Companion collector for UniFi UDM Pro API Monitoring. It adds per-client
traffic/RSSI, site DPI application traffic and controller-local Wi-Fi
connectivity metrics used by Zabbix-UniFi-Dashboard.

UniFi Network 10.6.x live validation established the following API-key
accessible controller-local v2 endpoints:
  /proxy/network/v2/api/site/<site>/traffic
  /proxy/network/v2/api/site/<site>/wifi-connectivity
  /proxy/network/v2/api/site/<site>/wifi-stats/radios

The v2 traffic endpoint expects start/end in Unix epoch milliseconds.
Only Python standard-library modules are required.
"""

import argparse
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "0.8.0-rc4"
DEFAULT_TIMEOUT = 20
DEFAULT_WINDOW = 86400
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
    rx = num(first(row, "rx_bytes", "rxBytes", "bytes_rx", "bytesRx", "bytes_received")) or 0
    tx = num(first(row, "tx_bytes", "txBytes", "bytes_tx", "bytesTx", "bytes_transmitted")) or 0
    usage = row.get("traffic_usage") or row.get("trafficUsage")
    if isinstance(usage, dict):
        rx = num(first(usage, "rx_bytes", "rxBytes", "downloadBytes", "bytes_received")) or rx
        tx = num(first(usage, "tx_bytes", "txBytes", "uploadBytes", "bytes_transmitted")) or tx
    return max(0, int(rx + tx))


def period(window):
    end = int(time.time())
    start = end - max(60, int(window))
    return start, end


def traffic_snapshot(base, key, site, timeout, verify, window):
    start, end = period(window)
    payload = req(
        v2(base, site, "traffic"), key,
        query={
            "start": start * 1000,
            "end": end * 1000,
            "includeUnidentified": "true"
        },
        timeout=timeout, verify=verify
    )
    return payload, start, end


def legacy_station_rows(base, key, site, timeout, verify):
    payload = req(
        legacy(base, site, "stat/sta"), key,
        query={"include_traffic_usage": "true"}, timeout=timeout, verify=verify
    )
    return [row for row in payload.get("data", []) if isinstance(row, dict)]


def normalized_station(row, traffic_bytes=None):
    cid = safe_id(first(row, "_id", "id", "client_id", "clientId", "mac"))
    if not cid:
        return None, None
    wired = first(row, "is_wired", "isWired", "wired")
    access = str(first(row, "type", "access_type", "accessType") or "").upper()
    wireless = (
        wired is False or str(wired).lower() in {"0", "false", "no"}
        or access == "WIRELESS"
        or any(row.get(k) not in (None, "") for k in ("essid", "radio", "ap_mac", "apMac"))
    )
    signal = rssi_dbm(row) if wireless else None
    return cid, {
        "name": str(first(row, "name", "hostname", "display_name", "displayName")
                    or row.get("oui") or row.get("mac") or cid),
        "mac": str(row.get("mac") or ""),
        "ip": str(first(row, "ip", "ipAddress") or ""),
        "wireless": wireless,
        "rssi": signal,
        "traffic_bytes": bytes_total(row) if traffic_bytes is None else max(0, int(traffic_bytes)),
        "ap_mac": str(first(row, "ap_mac", "apMac") or ""),
        "ssid": str(first(row, "essid", "ssid") or "")
    }


def clients(base, key, site, timeout, verify, window):
    result = {}
    signals = []
    source = "legacy/stat/sta"
    start = end = None

    # Keep the current station table for identity, RSSI, AP and SSID. Its
    # internal client id is preserved to avoid unnecessary Zabbix LLD churn.
    try:
        rows = legacy_station_rows(base, key, site, timeout, verify)
    except RequestError:
        rows = []

    station_by_mac = {}
    for row in rows:
        cid, station = normalized_station(row)
        if not cid or not station:
            continue
        result[cid] = station
        mac = str(station.get("mac") or "").lower()
        if mac:
            station_by_mac[mac] = cid

    try:
        payload, traffic_start, traffic_end = traffic_snapshot(
            base, key, site, timeout, verify, window
        )
        entries = [
            entry for entry in payload.get("client_usage_by_app", [])
            if isinstance(entry, dict)
        ]

        if entries:
            # Once v2 traffic is usable, all ranking values must come from the
            # same rolling window. Do not mix 24-hour v2 totals with legacy
            # counters for stations missing from client_usage_by_app.
            source = "v2/traffic"
            start, end = traffic_start, traffic_end
            for current in result.values():
                current["traffic_bytes"] = 0

            for entry in entries:
                client = entry.get("client") or {}
                mac = str(first(client, "mac", "macAddress") or "")
                cid = station_by_mac.get(mac.lower()) or safe_id(
                    mac or first(client, "id", "client_id", "clientId", "name", "hostname")
                )
                if not cid:
                    continue

                usage = entry.get("usage_by_app") or []
                total = sum(bytes_total(row) for row in usage if isinstance(row, dict))
                wired = first(client, "is_wired", "isWired", "wired")
                wireless = None if wired is None else (
                    wired is False or str(wired).lower() in {"0", "false", "no"}
                )
                client_name = first(client, "name", "hostname", "display_name", "displayName")

                if cid in result:
                    current = result[cid]
                    current["traffic_bytes"] += max(0, int(total))
                    if client_name:
                        current["name"] = str(client_name)
                    if wireless is not None:
                        current["wireless"] = wireless
                else:
                    result[cid] = {
                        "name": str(client_name or mac or cid),
                        "mac": mac,
                        "ip": str(first(client, "ip", "ipAddress") or ""),
                        "wireless": bool(wireless),
                        "rssi": None,
                        "traffic_bytes": max(0, int(total)),
                        "ap_mac": "",
                        "ssid": ""
                    }
    except RequestError:
        if not result:
            raise

    for client in result.values():
        signal = client.get("rssi")
        if signal is not None:
            signals.append(signal)

    if not result:
        raise RequestError("no client telemetry returned")

    ordered = sorted(signals)
    median = None
    if ordered:
        middle = len(ordered) // 2
        median = ordered[middle] if len(ordered) % 2 else round(
            (ordered[middle - 1] + ordered[middle]) / 2, 1
        )

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
            "critical": sum(v < -80 for v in signals),
            "traffic_source": source,
            "window_seconds": int(window) if source == "v2/traffic" else None,
            "start": start,
            "end": end
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


def compound_dpi_id(category, application):
    try:
        return (int(category) << 16) + int(application)
    except (TypeError, ValueError):
        return None


def dpi_v2(base, key, site, timeout, verify, window):
    payload, start, end = traffic_snapshot(base, key, site, timeout, verify, window)
    rows = [row for row in payload.get("total_usage_by_app", []) if isinstance(row, dict)]
    if not rows:
        raise RequestError("v2 traffic returned no DPI applications")

    catalog, apps = dpi_catalog(base, key, timeout, verify), {}
    for row in rows:
        category = first(row, "category", "category_id", "categoryId")
        application = first(row, "application", "app", "application_id", "applicationId", "appId")
        compound = compound_dpi_id(category, application)
        if compound is None:
            continue
        appid = safe_id(compound)

        rx = num(first(row, "bytes_received", "rx_bytes", "rxBytes", "bytes_rx", "bytesRx")) or 0
        tx = num(first(row, "bytes_transmitted", "tx_bytes", "txBytes", "bytes_tx", "bytesTx")) or 0
        total = num(first(row, "total_bytes", "totalBytes", "bytes", "num_bytes", "numBytes"))
        total = rx + tx if total is None else total

        try:
            unidentified = int(category) == 255 or int(application) == 65535
        except (TypeError, ValueError):
            unidentified = False
        fallback_name = "Unidentified / Unknown" if unidentified else f"App {category}/{application}"

        item = apps.setdefault(appid, {
            "name": catalog.get(appid) or fallback_name,
            "bytes": 0,
            "rx_bytes": 0,
            "tx_bytes": 0,
            "category": str(category),
            "application": str(application),
            "client_count": 0
        })
        item["bytes"] += max(0, int(total))
        item["rx_bytes"] += max(0, int(rx))
        item["tx_bytes"] += max(0, int(tx))
        item["client_count"] = max(
            item["client_count"], int(num(row.get("client_count")) or 0)
        )

    if not apps:
        raise RequestError("v2 traffic contained no usable DPI applications")

    return {
        "applications": apps,
        "summary": {
            "applications": len(apps),
            "bytes": sum(x["bytes"] for x in apps.values()),
            "traffic_source": "v2/traffic",
            "window_seconds": int(window),
            "start": start,
            "end": end
        }
    }


def dpi_legacy(base, key, site, timeout, verify):
    payload = req(
        legacy(base, site, "stat/sitedpi"), key, method="POST",
        payload={"type": "by_app"}, timeout=timeout, verify=verify
    )
    catalog, apps = dpi_catalog(base, key, timeout, verify), {}
    for row in payload.get("data", []):
        if not isinstance(row, dict):
            continue
        category = first(row, "cat", "category", "category_id", "categoryId")
        application = first(row, "app", "app_id", "appId", "application_id", "applicationId", "id")
        compound = compound_dpi_id(category, application) if category is not None else None
        appid = safe_id(compound if compound is not None else application)
        if not appid:
            continue

        rx = num(first(row, "rx_bytes", "rxBytes", "bytes_rx", "bytesRx")) or 0
        tx = num(first(row, "tx_bytes", "txBytes", "bytes_tx", "bytesTx")) or 0
        total = num(first(row, "bytes", "total_bytes", "totalBytes", "num_bytes", "numBytes"))
        total = rx + tx if total is None else total

        item = apps.setdefault(appid, {
            "name": str(first(row, "app_name", "appName", "name") or catalog.get(appid) or f"App {appid}"),
            "bytes": 0,
            "rx_bytes": 0,
            "tx_bytes": 0,
            "category": str(category or ""),
            "application": str(application or ""),
            "client_count": int(num(row.get("client_count")) or 0)
        })
        item["bytes"] += max(0, int(total))
        item["rx_bytes"] += max(0, int(rx))
        item["tx_bytes"] += max(0, int(tx))

    return {
        "applications": apps,
        "summary": {
            "applications": len(apps),
            "bytes": sum(x["bytes"] for x in apps.values()),
            "traffic_source": "legacy/stat/sitedpi"
        }
    }


def dpi(base, key, site, timeout, verify, window):
    try:
        return dpi_v2(base, key, site, timeout, verify, window)
    except RequestError:
        return dpi_legacy(base, key, site, timeout, verify)


ALIASES = {
    "association": {"association", "association_ratio", "association_success", "association_success_rate",
                    "association_success_pct", "associationsuccess", "associationsuccessrate",
                    "assoc_success", "assoc_success_rate", "assoc_success_pct"},
    "authentication": {"authentication", "authentication_ratio", "authentication_success",
                       "authentication_success_rate", "authentication_success_pct", "authenticationsuccess",
                       "authenticationsuccessrate", "auth_success", "auth_success_rate", "auth_success_pct"},
    "dhcp": {"dhcp", "dhcp_ratio", "dhcp_success", "dhcp_success_rate", "dhcp_success_pct",
             "dhcpsuccess", "dhcpsuccessrate"},
    "dns": {"dns", "dns_ratio", "dns_success", "dns_success_rate", "dns_success_pct",
            "dnssuccess", "dnssuccessrate"}
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


def wifi_performance(base, key, site, timeout, verify, window):
    del window
    endpoint = "v2/api/site/<site>/wifi-connectivity"
    try:
        payload = req(v2(base, site, "wifi-connectivity"), key, timeout=timeout, verify=verify)
    except RequestError as exc:
        return {
            "available": False,
            "endpoint": endpoint,
            "association": None,
            "authentication": None,
            "dhcp": None,
            "dns": None,
            "error": str(exc),
            "status": exc.status
        }

    attempts = payload.get("attempts") if isinstance(payload, dict) else None
    attempts = attempts if isinstance(attempts, dict) else {}
    metrics = {
        "association": num(attempts.get("association_ratio")),
        "authentication": num(attempts.get("authentication_ratio")),
        "dhcp": num(attempts.get("dhcp_ratio")),
        "dns": num(attempts.get("dns_ratio"))
    }
    for name, aliases in ALIASES.items():
        if metrics[name] is None:
            metrics[name] = find_metric(payload, aliases)
        if metrics[name] is not None:
            metrics[name] = round(metrics[name], 2)

    return {
        "available": any(v is not None for v in metrics.values()),
        "endpoint": endpoint,
        **metrics,
        "success": num(attempts.get("success_ratio")),
        "total_attempts": int(num(attempts.get("total_attempts")) or 0),
        "failed_client_connections": int(num(attempts.get("failed_client_connections")) or 0),
        "total_clients": int(num(payload.get("total_clients")) or 0) if isinstance(payload, dict) else 0,
        "latencies": payload.get("latencies", {}) if isinstance(payload, dict) else {}
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("clients", "dpi", "wifi-performance", "version"))
    parser.add_argument("base_url", nargs="?")
    parser.add_argument("api_key", nargs="?")
    parser.add_argument("site", nargs="?", default="default")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--window", type=int, default=DEFAULT_WINDOW,
                        help="rolling traffic/DPI window in seconds (default: 86400)")
    parser.add_argument("--verify-tls", action="store_true")

    # Zabbix can leave a user macro literal (for example {$UNIFI.TLS.ARG}) in
    # the command line when a macro defined only on a sibling linked template
    # is not resolved for this external item. Ignore only unresolved Zabbix
    # macro tokens so real command-line mistakes remain visible.
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
        func = {
            "clients": clients,
            "dpi": dpi,
            "wifi-performance": wifi_performance
        }[args.command]
        emit(func(args.base_url, args.api_key, args.site, args.timeout, args.verify_tls, args.window))
    except RequestError as exc:
        emit({"error": str(exc), "status": exc.status, "details": exc.details})
    except Exception as exc:
        emit({"error": "collector failure", "details": str(exc)})


if __name__ == "__main__":
    main()
