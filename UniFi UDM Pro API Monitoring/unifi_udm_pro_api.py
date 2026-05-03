#!/usr/bin/env python3
"""
UniFi UDM Pro API Monitoring
Version: 0.6.0

External script for Zabbix templates.

This collector intentionally uses only Python standard library modules so it can
run in the Zabbix external scripts directory without a virtual environment.

The project uses two UniFi Network API surfaces:

1. Integration API:
   /proxy/network/integration/v1

   This is the documented API key based interface used for sites, devices,
   clients, networks, and simple device details.

2. Legacy Network API:
   /proxy/network/api/s/<site>/...

   This endpoint is still available on the tested UDM Pro and exposes richer
   operational telemetry such as CPU, memory, storage, WAN statistics, and radio
   runtime counters. The script keeps this path isolated in dedicated helper
   functions so it remains easy to audit or disable if a future UniFi release
   changes behavior.

All commands return valid JSON or a scalar value suitable for Zabbix items. On
errors, JSON commands return {"error": "..."} and exit with code 0. This avoids
breaking dependent items with malformed output.
"""

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_LIMIT = 200


def is_blank_arg(value):
    """Return true for empty values and unresolved Zabbix user macros."""
    if value is None:
        return True
    text = str(value)
    return text == "" or (text.startswith("{$") and text.endswith("}"))


def print_json(payload):
    """Print compact JSON.

    Zabbix stores raw master item values frequently. Compact JSON reduces
    history size while keeping the payload valid for JSONPath preprocessing.
    """
    print(json.dumps(payload, separators=(",", ":"), sort_keys=True))


def fail(message, **extra):
    """Return a stable JSON error payload and stop.

    External scripts commonly fail because of TLS, firewall, credentials, or API
    changes. Returning JSON instead of raising a traceback makes failures visible
    in the master item without causing every dependent item to receive invalid
    text.
    """
    payload = {"error": message}
    payload.update(extra)
    print_json(payload)
    sys.exit(0)


def normalize_base_url(base_url):
    """Normalize the Integration API base URL.

    The template macro can contain either the UDM Pro root URL
    (https://<udm-pro-ip>) or the full integration prefix. Supporting both keeps
    manual testing comfortable and prevents duplicated path segments.
    """
    if is_blank_arg(base_url):
        fail("missing UniFi API URL")

    base_url = base_url.rstrip("/")
    if base_url.endswith("/proxy/network/integration/v1"):
        return base_url

    return base_url + "/proxy/network/integration/v1"


def normalize_root_url(base_url):
    """Normalize the UDM Pro root URL for non-Integration API paths."""
    if is_blank_arg(base_url):
        fail("missing UniFi API URL")

    base_url = base_url.rstrip("/")
    integration_suffix = "/proxy/network/integration/v1"
    if base_url.endswith(integration_suffix):
        return base_url[: -len(integration_suffix)]

    return base_url


def build_url(base_url, path, query=None):
    """Build a URL for the documented Integration API."""
    url = normalize_base_url(base_url) + "/" + path.lstrip("/")
    if query:
        url += "?" + urllib.parse.urlencode(query)
    return url


def build_legacy_url(base_url, legacy_site, path, query=None):
    """Build a URL for the legacy UniFi Network API.

    `legacy_site` is usually `default`, which matches the `internalReference`
    returned by the Integration API sites endpoint in single-site UDM Pro
    deployments.
    """
    if is_blank_arg(base_url):
        fail("missing UniFi API URL")

    legacy_site = "default" if is_blank_arg(legacy_site) else legacy_site
    base_url = normalize_root_url(base_url)
    path = path.lstrip("/")
    url = f"{base_url}/proxy/network/api/s/{urllib.parse.quote(legacy_site)}/{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    return url


def request_json(base_url, api_key, path, query=None, insecure=True, timeout=20):
    """Perform a GET request against the Integration API and parse JSON."""
    if is_blank_arg(api_key):
        fail("missing UniFi API key")

    req = urllib.request.Request(
        build_url(base_url, path, query),
        headers={
            "Accept": "application/json",
            "X-API-KEY": api_key,
        },
        method="GET",
    )

    context = None
    if insecure:
        context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        fail("http error", status=exc.code, details=details)
    except urllib.error.URLError as exc:
        fail("connection error", details=str(exc.reason))
    except TimeoutError:
        fail("request timed out")
    except Exception as exc:
        fail("request failed", details=str(exc))

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        fail("invalid JSON response", body=body[:500])


def request_legacy_json(base_url, api_key, legacy_site, path, query=None, insecure=True, timeout=20):
    """Perform a GET request against the legacy Network API and parse JSON."""
    if is_blank_arg(api_key):
        fail("missing UniFi API key")

    req = urllib.request.Request(
        build_legacy_url(base_url, legacy_site, path, query),
        headers={
            "Accept": "application/json",
            "X-API-KEY": api_key,
        },
        method="GET",
    )

    context = None
    if insecure:
        context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        fail("legacy http error", status=exc.code, details=details)
    except urllib.error.URLError as exc:
        fail("legacy connection error", details=str(exc.reason))
    except TimeoutError:
        fail("legacy request timed out")
    except Exception as exc:
        fail("legacy request failed", details=str(exc))

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        fail("invalid legacy JSON response", body=body[:500])


def paginated_get(base_url, api_key, path, insecure=True, timeout=20, limit=DEFAULT_LIMIT):
    """Read all pages from Integration API endpoints using offset/limit.

    Tested endpoints return objects like:
        {"offset": 0, "limit": 25, "count": 25, "totalCount": 28, "data": []}

    The function preserves the envelope but replaces `data` with the combined
    list from all pages.
    """
    items = []
    offset = 0
    last_payload = None

    while True:
        payload = request_json(
            base_url,
            api_key,
            path,
            query={"offset": offset, "limit": limit},
            insecure=insecure,
            timeout=timeout,
        )
        last_payload = payload

        data = payload.get("data")
        if not isinstance(data, list):
            return payload

        items.extend(data)

        count = int(payload.get("count", len(data)))
        total = int(payload.get("totalCount", len(items)))
        offset = int(payload.get("offset", offset)) + count

        if count <= 0 or offset >= total:
            break

    return {
        "offset": 0,
        "limit": limit,
        "count": len(items),
        "totalCount": last_payload.get("totalCount", len(items)) if last_payload else len(items),
        "data": items,
    }


def lld_item(macros):
    """Normalize low-level discovery macro values to strings.

    Zabbix LLD macros are text values. Booleans are normalized to lowercase so
    filters and overrides can compare against predictable `true`/`false`
    strings.
    """
    normalized = {}
    for key, value in macros.items():
        if value is None:
            normalized[key] = ""
        elif isinstance(value, bool):
            normalized[key] = "true" if value else "false"
        else:
            normalized[key] = str(value)
    return normalized


def discover_devices(payload):
    """Convert Integration API devices into Zabbix LLD rows."""
    data = payload.get("data", [])
    return {
        "data": [
            lld_item({
                "{#UNIFI.DEVICE.ID}": item.get("id"),
                "{#UNIFI.DEVICE.NAME}": item.get("name"),
                "{#UNIFI.DEVICE.MAC}": item.get("macAddress"),
                "{#UNIFI.DEVICE.IP}": item.get("ipAddress"),
                "{#UNIFI.DEVICE.MODEL}": item.get("model"),
                "{#UNIFI.DEVICE.STATE}": item.get("state"),
                "{#UNIFI.DEVICE.FIRMWARE}": item.get("firmwareVersion"),
                "{#UNIFI.DEVICE.SUPPORTED}": item.get("supported"),
                "{#UNIFI.DEVICE.UPDATABLE}": item.get("firmwareUpdatable"),
                "{#UNIFI.DEVICE.FEATURES}": ",".join(item.get("features", [])),
                "{#UNIFI.DEVICE.INTERFACES}": ",".join(item.get("interfaces", [])),
            })
            for item in data
        ]
    }


def discover_clients(payload):
    """Convert Integration API clients into Zabbix LLD rows."""
    data = payload.get("data", [])
    return {
        "data": [
            lld_item({
                "{#UNIFI.CLIENT.ID}": item.get("id"),
                "{#UNIFI.CLIENT.NAME}": item.get("name"),
                "{#UNIFI.CLIENT.TYPE}": item.get("type"),
                "{#UNIFI.CLIENT.MAC}": item.get("macAddress"),
                "{#UNIFI.CLIENT.IP}": item.get("ipAddress"),
                "{#UNIFI.CLIENT.UPLINK_DEVICE_ID}": item.get("uplinkDeviceId"),
                "{#UNIFI.CLIENT.ACCESS_TYPE}": (item.get("access") or {}).get("type"),
                "{#UNIFI.CLIENT.CONNECTED_AT}": item.get("connectedAt"),
            })
            for item in data
        ]
    }


def discover_networks(payload):
    """Convert Integration API networks/VLANs into Zabbix LLD rows."""
    data = payload.get("data", [])
    return {
        "data": [
            lld_item({
                "{#UNIFI.NETWORK.ID}": item.get("id"),
                "{#UNIFI.NETWORK.NAME}": item.get("name"),
                "{#UNIFI.NETWORK.ENABLED}": item.get("enabled"),
                "{#UNIFI.NETWORK.VLAN_ID}": item.get("vlanId"),
                "{#UNIFI.NETWORK.MANAGEMENT}": item.get("management"),
                "{#UNIFI.NETWORK.ORIGIN}": (item.get("metadata") or {}).get("origin"),
                "{#UNIFI.NETWORK.CONFIGURABLE}": (item.get("metadata") or {}).get("configurable"),
                "{#UNIFI.NETWORK.ZONE_ID}": item.get("zoneId"),
                "{#UNIFI.NETWORK.DEFAULT}": item.get("default"),
            })
            for item in data
        ]
    }


def discover_ports(payload):
    """Discover ports from a single Integration API device-detail payload."""
    device = payload
    ports = ((device.get("interfaces") or {}).get("ports") or [])
    return {
        "data": [
            lld_item({
                "{#UNIFI.DEVICE.ID}": device.get("id"),
                "{#UNIFI.DEVICE.NAME}": device.get("name"),
                "{#UNIFI.PORT.IDX}": port.get("idx"),
                "{#UNIFI.PORT.STATE}": port.get("state"),
                "{#UNIFI.PORT.CONNECTOR}": port.get("connector"),
                "{#UNIFI.PORT.MAX_SPEED}": port.get("maxSpeedMbps"),
                "{#UNIFI.PORT.SPEED}": port.get("speedMbps"),
            })
            for port in ports
        ]
    }


def discover_all_ports(base_url, api_key, site_id, insecure=True, timeout=20, limit=DEFAULT_LIMIT):
    """Discover ports across all devices that advertise a `ports` interface.

    The device list is cheap and tells us whether a detail call is worth making.
    This avoids querying APs for port data they do not expose.
    """
    devices = paginated_get(
        base_url,
        api_key,
        f"sites/{site_id}/devices",
        insecure=insecure,
        timeout=timeout,
        limit=limit,
    ).get("data", [])
    discovered = []

    for device in devices:
        interfaces = device.get("interfaces") or []
        if "ports" not in interfaces:
            continue

        detail = request_json(
            base_url,
            api_key,
            f"sites/{site_id}/devices/{device.get('id')}",
            insecure=insecure,
            timeout=timeout,
        )
        discovered.extend(discover_ports(detail).get("data", []))

    return {"data": discovered}


def discover_radios(payload):
    """Discover basic radio configuration from a single Integration API device."""
    device = payload
    radios = ((device.get("interfaces") or {}).get("radios") or [])
    return {
        "data": [
            lld_item({
                "{#UNIFI.DEVICE.ID}": device.get("id"),
                "{#UNIFI.DEVICE.NAME}": device.get("name"),
                "{#UNIFI.RADIO.INDEX}": index,
                "{#UNIFI.RADIO.STANDARD}": radio.get("wlanStandard"),
                "{#UNIFI.RADIO.FREQUENCY}": radio.get("frequencyGHz"),
                "{#UNIFI.RADIO.CHANNEL_WIDTH}": radio.get("channelWidthMHz"),
                "{#UNIFI.RADIO.CHANNEL}": radio.get("channel"),
            })
            for index, radio in enumerate(radios)
        ]
    }


def discover_all_radios(base_url, api_key, site_id, insecure=True, timeout=20, limit=DEFAULT_LIMIT):
    """Discover basic radio configuration across all APs."""
    devices = paginated_get(
        base_url,
        api_key,
        f"sites/{site_id}/devices",
        insecure=insecure,
        timeout=timeout,
        limit=limit,
    ).get("data", [])
    discovered = []

    for device in devices:
        interfaces = device.get("interfaces") or []
        if "radios" not in interfaces:
            continue

        detail = request_json(
            base_url,
            api_key,
            f"sites/{site_id}/devices/{device.get('id')}",
            insecure=insecure,
            timeout=timeout,
        )
        discovered.extend(discover_radios(detail).get("data", []))

    return {"data": discovered}


def legacy_discover_radios(payload):
    """Discover runtime radio rows from legacy `radio_table_stats`.

    These rows contain the useful Wi-Fi health indicators that resemble the
    UniFi controller radio/channel views: channel utilization, retries, station
    counts, and satisfaction.
    """
    discovered = []
    for device_id, device_radios in legacy_radios_document(payload).items():
        for index, radio in device_radios.items():
            discovered.append(lld_item({
                "{#UNIFI.DEVICE.ID}": device_id,
                "{#UNIFI.DEVICE.NAME}": radio.get("device_name"),
                "{#UNIFI.RADIO.INDEX}": index,
                "{#UNIFI.RADIO.NAME}": radio.get("name"),
                "{#UNIFI.RADIO.BAND}": radio.get("band"),
                "{#UNIFI.RADIO.CHANNEL}": radio.get("channel"),
                "{#UNIFI.RADIO.STATE}": radio.get("state"),
            }))
    return {"data": discovered}


def print_scalar(value):
    """Print a scalar value for simple Zabbix external items."""
    if value is None:
        print("")
    elif isinstance(value, bool):
        print("1" if value else "0")
    else:
        print(value)


def port_field(base_url, api_key, site_id, device_id, port_idx, field, insecure=True, timeout=20):
    """Return one port field from one Integration API device detail payload."""
    payload = request_json(
        base_url,
        api_key,
        f"sites/{site_id}/devices/{device_id}",
        insecure=insecure,
        timeout=timeout,
    )
    ports = ((payload.get("interfaces") or {}).get("ports") or [])
    for port in ports:
        if str(port.get("idx")) == str(port_idx):
            value = port.get(field)
            if field in {"speedMbps", "maxSpeedMbps"} and value in (None, ""):
                print_scalar(0)
                return
            print_scalar(value)
            return
    print_scalar(None)


def radio_field(base_url, api_key, site_id, device_id, radio_index, field, insecure=True, timeout=20):
    """Return one basic radio field from one Integration API device detail payload."""
    payload = request_json(
        base_url,
        api_key,
        f"sites/{site_id}/devices/{device_id}",
        insecure=insecure,
        timeout=timeout,
    )
    radios = ((payload.get("interfaces") or {}).get("radios") or [])
    try:
        radio = radios[int(radio_index)]
    except (IndexError, TypeError, ValueError):
        print_scalar(None)
        return
    print_scalar(radio.get(field))


def legacy_radio_field(device, radio_index, field):
    """Return one runtime radio field from `radio_table_stats`."""
    radios = device.get("radio_table_stats") or []
    try:
        radio = radios[int(radio_index)]
    except (IndexError, TypeError, ValueError):
        print_scalar(None)
        return

    value = radio.get(field)
    if field == "satisfaction" and to_float(value, 0.0) < 0:
        print_scalar(0)
        return

    print_scalar(value)


def legacy_radio_value(radio, field):
    """Return normalized legacy radio metrics for Zabbix items."""
    if field in {"cu_total", "cu_self_rx", "cu_self_tx", "tx_retries_pct", "satisfaction"}:
        value = to_float(radio.get(field))
        if field == "satisfaction" and value < 0:
            return 0
        return value
    if field == "num_sta":
        return to_int(radio.get(field))
    return radio.get(field)


def legacy_radios_document(payload):
    """Build a compact device/radio map for dependent item prototypes."""
    document = {}
    fields = (
        "cu_total",
        "cu_self_rx",
        "cu_self_tx",
        "tx_retries_pct",
        "num_sta",
        "satisfaction",
    )

    for device in legacy_devices(payload):
        device_id = str(device.get("external_id") or device.get("_id") or device.get("device_id") or device.get("mac") or "")
        if not device_id:
            continue

        radios = device.get("radio_table_stats") or []
        device_radios = document.setdefault(device_id, {})
        for index, radio in enumerate(radios):
            item = {
                "device_name": device.get("name") or "",
                "device_model": device.get("model") or "",
                "name": radio.get("name") or "",
                "band": radio.get("radio") or "",
                "channel": radio.get("channel"),
                "state": radio.get("state") or "",
            }
            for field in fields:
                item[field] = legacy_radio_value(radio, field)
            device_radios[str(index)] = item

    return document


def first_value(mapping, *keys):
    """Return the first non-empty value from a mapping."""
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return None


def legacy_port_index(port):
    """Return the most stable port index exposed by legacy port tables."""
    return first_value(port, "port_idx", "idx", "port", "port_id")


def legacy_ports(device):
    """Return the legacy `port_table` list safely."""
    ports = device.get("port_table") or []
    return ports if isinstance(ports, list) else []


def legacy_discover_ports(payload):
    """Discover richer switch/gateway ports from legacy `port_table` data."""
    discovered = []
    for device_id, device_ports in legacy_ports_document(payload).items():
        for port_idx, port in device_ports.items():
            discovered.append(lld_item({
                "{#UNIFI.DEVICE.ID}": device_id,
                "{#UNIFI.DEVICE.NAME}": port.get("device_name"),
                "{#UNIFI.DEVICE.MODEL}": port.get("device_model"),
                "{#UNIFI.PORT.IDX}": port_idx,
                "{#UNIFI.PORT.NAME}": port.get("name"),
                "{#UNIFI.PORT.IFNAME}": port.get("ifname"),
                "{#UNIFI.PORT.POE_MODE}": port.get("poe_mode"),
            }))
    return {"data": discovered}


def legacy_port_value(port, field):
    """Return normalized legacy port metrics for Zabbix items."""
    if field == "up":
        return to_bool(first_value(port, "up", "link", "link_up"))
    if field == "speed_mbps":
        return to_float(first_value(port, "speed", "speedMbps", "speed_mbps"))
    if field == "rx_bps":
        return round(to_float(first_value(port, "rx_bytes-r", "rx_bytes_rate", "rx_rate")) * 8, 2)
    if field == "tx_bps":
        return round(to_float(first_value(port, "tx_bytes-r", "tx_bytes_rate", "tx_rate")) * 8, 2)
    if field == "rx_errors":
        return to_int(first_value(port, "rx_errors", "rx_error", "rx_errors_delta"))
    if field == "tx_errors":
        return to_int(first_value(port, "tx_errors", "tx_error", "tx_errors_delta"))
    if field == "rx_dropped":
        return to_int(first_value(port, "rx_dropped", "rx_drops", "rx_drop"))
    if field == "tx_dropped":
        return to_int(first_value(port, "tx_dropped", "tx_drops", "tx_drop"))
    if field == "poe_power_w":
        return to_float(first_value(port, "poe_power", "poe_power_w"))
    if field == "poe_voltage_v":
        return to_float(first_value(port, "poe_voltage", "poe_voltage_v"))
    if field == "poe_good":
        return to_bool(first_value(port, "poe_good", "poe_enable", "poe_power"))
    if field == "poe_mode":
        return first_value(port, "poe_mode", "poe_caps")
    if field == "name":
        return first_value(port, "name", "ifname", "label")
    return port.get(field)


def legacy_port_field(device, port_idx, field):
    """Print one scalar field from a legacy `port_table` row."""
    for port in legacy_ports(device):
        if str(legacy_port_index(port)) == str(port_idx):
            print_scalar(legacy_port_value(port, field))
            return
    print_scalar(None)


def legacy_ports_document(payload):
    """Build a compact device/port map for dependent item prototypes."""
    document = {}
    fields = (
        "up",
        "speed_mbps",
        "rx_bps",
        "tx_bps",
        "rx_errors",
        "tx_errors",
        "rx_dropped",
        "tx_dropped",
        "poe_power_w",
        "poe_voltage_v",
        "poe_good",
        "poe_mode",
    )

    for device in legacy_devices(payload):
        device_id = str(device.get("external_id") or device.get("_id") or device.get("device_id") or device.get("mac") or "")
        if not device_id:
            continue

        device_ports = document.setdefault(device_id, {})
        for port in legacy_ports(device):
            port_idx = legacy_port_index(port)
            if port_idx is None:
                continue

            port_idx = str(port_idx)
            item = {
                "device_name": device.get("name") or "",
                "device_model": device.get("model") or "",
                "name": legacy_port_value(port, "name") or "",
                "ifname": first_value(port, "ifname", "name") or "",
            }
            for field in fields:
                item[field] = legacy_port_value(port, field)
            device_ports[port_idx] = item

    return document


def legacy_stat_devices(base_url, api_key, legacy_site, insecure=True, timeout=20):
    """Fetch the legacy stat/device payload for the selected site."""
    return request_legacy_json(base_url, api_key, legacy_site, "stat/device", insecure=insecure, timeout=timeout)


def legacy_devices(payload):
    """Return the legacy device list safely."""
    data = payload.get("data", [])
    return data if isinstance(data, list) else []


def find_legacy_device(payload, device_id=None):
    """Find a legacy device by common identifiers.

    For UDM-level system/WAN metrics, the caller can omit `device_id`; in that
    case the first legacy device with type `udm` or model `UDMPRO` is selected.
    """
    devices = legacy_devices(payload)
    if is_blank_arg(device_id):
        device_id = None

    if device_id:
        for device in devices:
            identifiers = {
                str(device.get("external_id", "")),
                str(device.get("_id", "")),
                str(device.get("device_id", "")),
                str(device.get("mac", "")),
                str(device.get("name", "")),
            }
            if str(device_id) in identifiers:
                return device
        fail("legacy device not found", device_id=device_id)

    for device in devices:
        if device.get("type") == "udm" or device.get("model") == "UDMPRO":
            return device

    if len(devices) == 1:
        return devices[0]

    fail("legacy device ID is required")


def to_float(value, default=0.0):
    """Best-effort float conversion for inconsistent UniFi numeric fields."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value, default=0):
    """Best-effort integer conversion for counters that may arrive as strings."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def to_bool(value, default=False):
    """Best-effort boolean conversion for inconsistent UniFi status fields."""
    if value is None or value == "":
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value != 0

    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on", "up", "enabled", "enable", "good", "ok"}:
        return True
    if text in {"0", "false", "no", "n", "off", "down", "disabled", "disable", "bad"}:
        return False

    try:
        return float(text) != 0
    except ValueError:
        pass

    return default


def system_health(device):
    """Build a compact system-health document from one legacy device.

    The UDM Pro exposes CPU/memory percentages under `system-stats`, raw memory
    counters under `sys_stats`, and storage/temperature arrays as top-level
    lists. This function flattens those shapes into stable keys for dependent
    Zabbix items.
    """
    system_stats = device.get("system-stats") or {}
    sys_stats = device.get("sys_stats") or {}
    storage = device.get("storage") or []
    temperatures = device.get("temperatures") or []

    storage_size = sum(to_int(item.get("size")) for item in storage)
    storage_used = sum(to_int(item.get("used")) for item in storage)
    storage_free = max(0, storage_size - storage_used)
    storage_used_percent = (storage_used / storage_size * 100) if storage_size else 0

    result = {
        "cpu_percent": to_float(system_stats.get("cpu")),
        "memory_percent": to_float(system_stats.get("mem")),
        "uptime": to_int(system_stats.get("uptime") or device.get("uptime")),
        "loadavg_1": to_float(sys_stats.get("loadavg_1")),
        "loadavg_5": to_float(sys_stats.get("loadavg_5")),
        "loadavg_15": to_float(sys_stats.get("loadavg_15")),
        "memory_total": to_int(sys_stats.get("mem_total")),
        "memory_used": to_int(sys_stats.get("mem_used")),
        "memory_buffer": to_int(sys_stats.get("mem_buffer")),
        "storage_total": storage_size,
        "storage_used": storage_used,
        "storage_free": storage_free,
        "storage_used_percent": round(storage_used_percent, 2),
        "storage_count": len(storage),
        "temperature_count": len(temperatures),
    }

    for item in temperatures:
        temp_type = item.get("type") or item.get("name")
        if temp_type:
            result[f"temperature_{temp_type}"] = to_float(item.get("value"))

    return result


def discover_storage(device):
    """Discover storage volumes from a legacy UDM device."""
    storage = device.get("storage") or []
    return {
        "data": [
            lld_item({
                "{#UNIFI.STORAGE.NAME}": item.get("name"),
                "{#UNIFI.STORAGE.MOUNT}": item.get("mount_point"),
                "{#UNIFI.STORAGE.TYPE}": item.get("type"),
            })
            for item in storage
        ]
    }


def storage_field(device, mount_point, field):
    """Return one storage field by mount point."""
    storage = device.get("storage") or []
    for item in storage:
        if item.get("mount_point") == mount_point:
            if field == "free":
                print_scalar(to_int(item.get("size")) - to_int(item.get("used")))
                return
            if field == "used_percent":
                size = to_int(item.get("size"))
                used = to_int(item.get("used"))
                print_scalar(round(used / size * 100, 2) if size else 0)
                return
            print_scalar(item.get(field))
            return
    print_scalar(None)


def wan_candidates(device):
    """Return the WAN names exposed by the legacy payload.

    A single-WAN UDM usually exposes keys such as `WAN`, `wan1`, and `uplink`.
    Multi-WAN systems may add `WAN2`, `wan2`, or additional entries under
    `last_wan_interfaces`. The returned names are normalized to the controller
    labels (`WAN`, `WAN2`, ...), which are stable LLD macro values.
    """
    names = set()

    for name in (device.get("uptime_stats") or {}).keys():
        if str(name).upper().startswith("WAN"):
            names.add(str(name).upper())

    for name in (device.get("last_wan_interfaces") or {}).keys():
        if str(name).upper().startswith("WAN"):
            names.add(str(name).upper())

    for key in device.keys():
        key_text = str(key).lower()
        if key_text.startswith("wan") and key_text[3:].isdigit():
            suffix = key_text[3:]
            names.add("WAN" if suffix == "1" else f"WAN{suffix}")

    if device.get("uplink"):
        names.add("WAN")

    return sorted(names, key=lambda name: (len(name), name))


def wan_source(device, wan_name):
    """Collect the legacy structures that describe one WAN link."""
    wan_name = (wan_name or "WAN").upper()
    wan_number = "1" if wan_name == "WAN" else wan_name.replace("WAN", "", 1)

    uptime_stats = ((device.get("uptime_stats") or {}).get(wan_name) or {})
    interface_state = ((device.get("last_wan_interfaces") or {}).get(wan_name) or {})
    wan_table = device.get(f"wan{wan_number}") or {}
    uplink = device.get("uplink") or {}

    # On single-WAN systems, the `uplink` object is the most complete active WAN
    # representation. For WAN2+, prefer the numbered `wanN` object when present.
    if wan_name != "WAN" and wan_table:
        uplink = wan_table

    return uptime_stats, interface_state, wan_table, uplink


def discover_wans(device):
    """Discover WAN links from the legacy UDM payload."""
    discovered = []
    for wan_name in wan_candidates(device):
        _, interface_state, wan_table, uplink = wan_source(device, wan_name)
        discovered.append(lld_item({
            "{#UNIFI.WAN.NAME}": wan_name,
            "{#UNIFI.WAN.IFNAME}": uplink.get("name") or wan_table.get("ifname") or wan_table.get("name"),
            "{#UNIFI.WAN.IP}": interface_state.get("ip") or uplink.get("ip") or wan_table.get("ip"),
            "{#UNIFI.WAN.ALIVE}": interface_state.get("alive"),
        }))
    return {"data": discovered}


def wan_health(device, wan_name="WAN"):
    """Return WAN health for one WAN label.

    The default remains `WAN` so existing single-WAN template items keep working.
    Multi-WAN item prototypes call the same function through `wan_field`.
    """
    uptime_stats, interface_state, wan_table, uplink = wan_source(device, wan_name)
    speedtest = device.get("speedtest-status") or {}
    speedtest_last_run = to_int(speedtest.get("rundate") or uplink.get("speedtest_lastrun"))
    speedtest_age = int(time.time()) - speedtest_last_run if speedtest_last_run else 0

    availability = to_float(uptime_stats.get("availability"), 0.0)
    rx_bps = to_float(uplink.get("rx_bytes-r")) * 8
    tx_bps = to_float(uplink.get("tx_bytes-r")) * 8
    alive = interface_state.get("alive")
    if alive is None:
        alive = uplink.get("up", False)

    return {
        "name": (wan_name or "WAN").upper(),
        "ifname": uplink.get("name") or wan_table.get("ifname") or wan_table.get("name") or "",
        "ip": interface_state.get("ip") or uplink.get("ip") or wan_table.get("ip") or "",
        "alive": to_bool(alive),
        "availability_percent": availability,
        "packet_loss_percent": round(max(0.0, 100.0 - availability), 4),
        "latency_ms": to_float(uptime_stats.get("latency_average") or uplink.get("latency")),
        "uptime_seconds": to_int(uplink.get("uptime")),
        "rx_bps": round(rx_bps, 2),
        "tx_bps": round(tx_bps, 2),
        "rx_mbps": round(rx_bps / 1000000, 4),
        "tx_mbps": round(tx_bps / 1000000, 4),
        "speed_mbps": to_float(uplink.get("speed")),
        "max_speed_mbps": to_float(uplink.get("max_speed")),
        "speedtest_download_mbps": to_float(speedtest.get("xput_download") or uplink.get("xput_down")),
        "speedtest_upload_mbps": to_float(speedtest.get("xput_upload") or uplink.get("xput_up")),
        "speedtest_latency_ms": to_float(speedtest.get("latency") or speedtest.get("speedtest_ping")),
        "speedtest_last_run": speedtest_last_run,
        "speedtest_age_seconds": speedtest_age,
        "speedtest_status": uplink.get("speedtest_status") or speedtest.get("status_summary") or "",
    }


def wan_field(device, wan_name, field):
    """Print one scalar field from a WAN health document."""
    print_scalar(wan_health(device, wan_name).get(field))


def summarize(payload, field):
    data = payload.get("data", [])
    if field == "devices":
        online = sum(1 for item in data if item.get("state") == "ONLINE")
        updatable = sum(1 for item in data if item.get("firmwareUpdatable") is True)
        return {"total": len(data), "online": online, "offline": len(data) - online, "updatable": updatable}
    if field == "clients":
        wired = sum(1 for item in data if item.get("type") == "WIRED")
        wireless = sum(1 for item in data if item.get("type") == "WIRELESS")
        return {"total": len(data), "wired": wired, "wireless": wireless}
    if field == "networks":
        enabled = sum(1 for item in data if item.get("enabled") is True)
        return {"total": len(data), "enabled": enabled, "disabled": len(data) - enabled}
    return {"total": len(data)}


def resolve_site_id(base_url, api_key, site_id, insecure=True, timeout=20, limit=DEFAULT_LIMIT):
    if not is_blank_arg(site_id):
        return site_id

    payload = paginated_get(base_url, api_key, "sites", insecure=insecure, timeout=timeout, limit=limit)
    sites = payload.get("data", [])
    if len(sites) == 1 and sites[0].get("id"):
        return sites[0]["id"]

    if not sites:
        fail("missing site ID and no sites were returned")

    fail("missing site ID and multiple sites were returned", sites=len(sites))


def parse_args():
    parser = argparse.ArgumentParser(description="Collect UniFi UDM Pro API data for Zabbix.")
    parser.add_argument("command", help="Command to run.")
    parser.add_argument("values", nargs="*", help="Optional URL/key/site/object arguments.")
    parser.add_argument("--verify-tls", action="store_true", help="Verify TLS certificates.")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    args = parser.parse_args()

    args.base_url = os.getenv("UNIFI_API_URL")
    args.api_key = os.getenv("UNIFI_API_KEY")
    args.site_id = os.getenv("UNIFI_SITE_ID")
    args.object_id = None

    object_commands = {"device", "client", "discover-ports", "discover-radios"}
    optional_legacy_device_commands = {"system-health", "wan-health", "discover-wans", "discover-storage"}

    args.extra_values = []

    if len(args.values) == 1 and args.command in object_commands:
        args.object_id = args.values[0]
    elif len(args.values) >= 2 and args.command == "info":
        args.base_url = args.values[0]
        args.api_key = args.values[1]
    elif len(args.values) >= 3:
        args.base_url = args.values[0]
        args.api_key = args.values[1]
        args.site_id = args.values[2]
        if args.command == "storage-field":
            if len(args.values) == 5:
                # Storage field calls can auto-select the UDM device:
                # url, key, legacy_site, mount_point, field.
                args.extra_values = args.values[3:]
            elif len(args.values) >= 6:
                # Backward compatibility for an explicit device ID:
                # url, key, legacy_site, device_id, mount_point, field.
                args.object_id = None if is_blank_arg(args.values[3]) else args.values[3]
                args.extra_values = args.values[4:]
            else:
                fail("invalid argument count", command=args.command, count=len(args.values))
        elif args.command == "wan-field":
            if len(args.values) == 5:
                # WAN field calls do not need a device ID because the script can
                # auto-select the UDM device from the legacy payload. This
                # accepts: url, key, legacy_site, wan_name, field.
                args.extra_values = args.values[3:]
            elif len(args.values) >= 6:
                # Backward compatibility for older template keys:
                # url, key, legacy_site, device_id, wan_name, field.
                args.object_id = None if is_blank_arg(args.values[3]) else args.values[3]
                args.extra_values = args.values[4:]
            else:
                fail("invalid argument count", command=args.command, count=len(args.values))
        elif args.command == "wan-health" and len(args.values) == 4:
            # Accept either a device ID or a WAN label as the fourth argument.
            # WAN labels always start with "WAN"; anything else is treated as a
            # device identifier.
            if str(args.values[3]).upper().startswith("WAN"):
                args.extra_values = [args.values[3]]
            else:
                args.object_id = None if is_blank_arg(args.values[3]) else args.values[3]
        elif args.command in optional_legacy_device_commands and len(args.values) >= 4:
            args.object_id = None if is_blank_arg(args.values[3]) else args.values[3]
            if len(args.values) >= 5:
                args.extra_values = args.values[4:]
        elif len(args.values) >= 4:
            args.object_id = None if is_blank_arg(args.values[3]) else args.values[3]
            if len(args.values) >= 5:
                args.extra_values = args.values[4:]
    elif args.values:
        fail("invalid argument count", command=args.command, count=len(args.values))

    return args


def main():
    args = parse_args()
    command = args.command
    insecure = not args.verify_tls

    if command == "info":
        print_json(request_json(args.base_url, args.api_key, "info", insecure=insecure, timeout=args.timeout))
        return

    if command == "sites":
        print_json(paginated_get(args.base_url, args.api_key, "sites", insecure=insecure, timeout=args.timeout, limit=args.limit))
        return

    if command == "legacy-devices":
        legacy_site = args.site_id or "default"
        print_json(legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout))
        return

    if command == "system-health":
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        print_json(system_health(find_legacy_device(payload, args.object_id)))
        return

    if command == "wan-health":
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        wan_name = args.extra_values[0] if args.extra_values else "WAN"
        print_json(wan_health(find_legacy_device(payload, args.object_id), wan_name))
        return

    if command == "discover-wans":
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        print_json(discover_wans(find_legacy_device(payload, args.object_id)))
        return

    if command == "discover-storage":
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        print_json(discover_storage(find_legacy_device(payload, args.object_id)))
        return

    if command == "legacy-discover-radios":
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        print_json(legacy_discover_radios(payload))
        return

    if command == "legacy-radios":
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        print_json(legacy_radios_document(payload))
        return

    if command == "legacy-discover-ports":
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        print_json(legacy_discover_ports(payload))
        return

    if command == "legacy-ports":
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        print_json(legacy_ports_document(payload))
        return

    if command == "legacy-port-field":
        if not args.object_id or len(args.extra_values) < 2:
            fail("missing legacy port field arguments")
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        legacy_port_field(find_legacy_device(payload, args.object_id), args.extra_values[0], args.extra_values[1])
        return

    if command == "storage-field":
        if len(args.extra_values) < 2:
            fail("missing storage field arguments")
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        storage_field(find_legacy_device(payload, args.object_id), args.extra_values[0], args.extra_values[1])
        return

    if command == "legacy-radio-field":
        if not args.object_id or len(args.extra_values) < 2:
            fail("missing legacy radio field arguments")
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        legacy_radio_field(find_legacy_device(payload, args.object_id), args.extra_values[0], args.extra_values[1])
        return

    if command == "wan-field":
        if len(args.extra_values) < 2:
            fail("missing WAN field arguments")
        legacy_site = args.site_id or "default"
        payload = legacy_stat_devices(args.base_url, args.api_key, legacy_site, insecure=insecure, timeout=args.timeout)
        wan_field(find_legacy_device(payload, args.object_id), args.extra_values[0], args.extra_values[1])
        return

    args.site_id = resolve_site_id(
        args.base_url,
        args.api_key,
        args.site_id,
        insecure=insecure,
        timeout=args.timeout,
        limit=args.limit,
    )

    collection_paths = {
        "devices": f"sites/{args.site_id}/devices",
        "clients": f"sites/{args.site_id}/clients",
        "networks": f"sites/{args.site_id}/networks",
    }

    if command in collection_paths:
        print_json(paginated_get(args.base_url, args.api_key, collection_paths[command], insecure=insecure, timeout=args.timeout, limit=args.limit))
        return

    if command == "device":
        if not args.object_id:
            fail("missing device ID")
        print_json(request_json(args.base_url, args.api_key, f"sites/{args.site_id}/devices/{args.object_id}", insecure=insecure, timeout=args.timeout))
        return

    if command == "client":
        if not args.object_id:
            fail("missing client ID")
        print_json(request_json(args.base_url, args.api_key, f"sites/{args.site_id}/clients/{args.object_id}", insecure=insecure, timeout=args.timeout))
        return

    if command == "discover-devices":
        payload = paginated_get(args.base_url, args.api_key, collection_paths["devices"], insecure=insecure, timeout=args.timeout, limit=args.limit)
        print_json(discover_devices(payload))
        return

    if command == "discover-clients":
        payload = paginated_get(args.base_url, args.api_key, collection_paths["clients"], insecure=insecure, timeout=args.timeout, limit=args.limit)
        print_json(discover_clients(payload))
        return

    if command == "discover-networks":
        payload = paginated_get(args.base_url, args.api_key, collection_paths["networks"], insecure=insecure, timeout=args.timeout, limit=args.limit)
        print_json(discover_networks(payload))
        return

    if command == "discover-ports":
        if args.object_id:
            payload = request_json(args.base_url, args.api_key, f"sites/{args.site_id}/devices/{args.object_id}", insecure=insecure, timeout=args.timeout)
            print_json(discover_ports(payload))
        else:
            print_json(discover_all_ports(args.base_url, args.api_key, args.site_id, insecure=insecure, timeout=args.timeout, limit=args.limit))
        return

    if command == "discover-radios":
        if args.object_id:
            payload = request_json(args.base_url, args.api_key, f"sites/{args.site_id}/devices/{args.object_id}", insecure=insecure, timeout=args.timeout)
            print_json(discover_radios(payload))
        else:
            print_json(discover_all_radios(args.base_url, args.api_key, args.site_id, insecure=insecure, timeout=args.timeout, limit=args.limit))
        return

    if command == "port-field":
        if not args.object_id or len(args.extra_values) < 2:
            fail("missing port field arguments")
        port_field(
            args.base_url,
            args.api_key,
            args.site_id,
            args.object_id,
            args.extra_values[0],
            args.extra_values[1],
            insecure=insecure,
            timeout=args.timeout,
        )
        return

    if command == "radio-field":
        if not args.object_id or len(args.extra_values) < 2:
            fail("missing radio field arguments")
        radio_field(
            args.base_url,
            args.api_key,
            args.site_id,
            args.object_id,
            args.extra_values[0],
            args.extra_values[1],
            insecure=insecure,
            timeout=args.timeout,
        )
        return

    if command == "summary-devices":
        payload = paginated_get(args.base_url, args.api_key, collection_paths["devices"], insecure=insecure, timeout=args.timeout, limit=args.limit)
        print_json(summarize(payload, "devices"))
        return

    if command == "summary-clients":
        payload = paginated_get(args.base_url, args.api_key, collection_paths["clients"], insecure=insecure, timeout=args.timeout, limit=args.limit)
        print_json(summarize(payload, "clients"))
        return

    if command == "summary-networks":
        payload = paginated_get(args.base_url, args.api_key, collection_paths["networks"], insecure=insecure, timeout=args.timeout, limit=args.limit)
        print_json(summarize(payload, "networks"))
        return

    fail("unknown command", command=command)


if __name__ == "__main__":
    main()
