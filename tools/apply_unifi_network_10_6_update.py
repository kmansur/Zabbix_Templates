#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path("UniFi UDM Pro API Monitoring")


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"Missing anchor: {label}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Collector 0.7.0: add a first-class command for the official Integration API
# statistics/latest endpoint. Existing legacy commands remain untouched.
# ---------------------------------------------------------------------------
script_path = ROOT / "unifi_udm_pro_api.py"
script = script_path.read_text(encoding="utf-8")
script = replace_once(script, "Version: 0.6.10", "Version: 0.7.0", "collector version")
script = replace_once(
    script,
    "   clients, networks, and simple device details.\n",
    "   clients, networks, simple device details, and the documented\n"
    "   devices/{deviceId}/statistics/latest real-time statistics endpoint.\n",
    "collector Integration API description",
)
script = replace_once(
    script,
    '    object_commands = {"device", "client", "discover-ports", "discover-radios"}\n',
    '    object_commands = {"device", "device-stats", "client", "discover-ports", "discover-radios"}\n',
    "collector object command set",
)
device_block = '''    if command == "device":
        if not args.object_id:
            fail("missing device ID")
        print_json(request_json(args.base_url, args.api_key, f"sites/{args.site_id}/devices/{args.object_id}", insecure=insecure, timeout=args.timeout))
        return

'''
device_stats_block = device_block + '''    if command == "device-stats":
        if not args.object_id:
            fail("missing device ID")
        print_json(request_json(
            args.base_url,
            args.api_key,
            f"sites/{args.site_id}/devices/{args.object_id}/statistics/latest",
            insecure=insecure,
            timeout=args.timeout,
        ))
        return

'''
script = replace_once(script, device_block, device_stats_block, "collector device command")
script_path.write_text(script, encoding="utf-8")


# ---------------------------------------------------------------------------
# Templates 7.0 and 8.0.
# ---------------------------------------------------------------------------
OFFICIAL_RULE = '''        - uuid: e86189358b09410cbd3062534c4f1826
          name: 'UniFi official gateway statistics discovery'
          type: EXTERNAL
          key: 'unifi_udm_pro_api.py["discover-devices","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{$UNIFI.TLS.ARG}"]'
          delay: 1h
          filter:
            evaltype: AND
            conditions:
              - macro: '{#UNIFI.DEVICE.MODEL}'
                value: '{$UNIFI.LLD.OFFICIAL.STATS.MODEL.MATCHES}'
          lifetime: 30d
          description: 'Discovers gateway-class devices for parallel monitoring through the documented Integration API statistics/latest endpoint.'
          item_prototypes:
            - uuid: 6b4f2306172147f58ebdfb321ad5279d
              name: 'Official API statistics raw on {#UNIFI.DEVICE.NAME}'
              type: EXTERNAL
              key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              delay: 2m
              history: 7d
              value_type: TEXT
              description: 'Raw snapshot from the documented /devices/{deviceId}/statistics/latest Integration API endpoint.'
              timeout: 30s
              tags:
                - tag: component
                  value: official-api
                - tag: device
                  value: '{#UNIFI.DEVICE.NAME}'
            - uuid: e0d412ab49234f98908725467f3ebdeb
              name: 'Official API statistics available on {#UNIFI.DEVICE.NAME}'
              type: DEPENDENT
              key: 'unifi.official.stats.available[{#UNIFI.DEVICE.ID}]'
              history: 90d
              preprocessing:
                - type: JAVASCRIPT
                  parameters:
                    - 'try { var data = JSON.parse(value); return data.error ? 0 : 1; } catch (e) { return 0; }'
              master_item:
                key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              tags:
                - tag: component
                  value: collector
                - tag: source
                  value: official-api
              trigger_prototypes:
                - uuid: 85b8f6b202324b52a5de1b704b40da1a
                  expression: 'max(/UniFi UDM Pro API Monitoring/unifi.official.stats.available[{#UNIFI.DEVICE.ID}],10m)=0'
                  name: 'Official UniFi statistics collection is failing on {#UNIFI.DEVICE.NAME}'
                  priority: WARNING
                  description: 'The documented Integration API statistics/latest endpoint is returning an error or invalid JSON.'
            - uuid: 4bad6b05cce4485ebc33f857757f9455
              name: 'Official API statistics last error on {#UNIFI.DEVICE.NAME}'
              type: DEPENDENT
              key: 'unifi.official.stats.error[{#UNIFI.DEVICE.ID}]'
              history: 30d
              value_type: TEXT
              preprocessing:
                - type: JAVASCRIPT
                  parameters:
                    - 'try { var data = JSON.parse(value); if (!data.error) { return ""; } return data.error + (data.details ? ": " + data.details : ""); } catch (e) { return "invalid JSON: " + e.message; }'
              master_item:
                key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              tags:
                - tag: component
                  value: collector
                - tag: source
                  value: official-api
            - uuid: 77218585aa6349b69f27edf259196fc9
              name: 'Official CPU utilization on {#UNIFI.DEVICE.NAME}'
              type: DEPENDENT
              key: 'unifi.official.system.cpu.percent[{#UNIFI.DEVICE.ID}]'
              history: 90d
              value_type: FLOAT
              units: '%'
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - $.cpuUtilizationPct
              master_item:
                key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              tags:
                - tag: component
                  value: system
                - tag: source
                  value: official-api
            - uuid: ae5a1820d1744f13849cb17eec8e8ddf
              name: 'Official memory utilization on {#UNIFI.DEVICE.NAME}'
              type: DEPENDENT
              key: 'unifi.official.system.memory.percent[{#UNIFI.DEVICE.ID}]'
              history: 90d
              value_type: FLOAT
              units: '%'
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - $.memoryUtilizationPct
              master_item:
                key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              tags:
                - tag: component
                  value: system
                - tag: source
                  value: official-api
            - uuid: 7ab2b460e70e4550908530eaa74f293b
              name: 'Official load average 1m on {#UNIFI.DEVICE.NAME}'
              type: DEPENDENT
              key: 'unifi.official.system.loadavg_1[{#UNIFI.DEVICE.ID}]'
              history: 90d
              value_type: FLOAT
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - $.loadAverage1Min
              master_item:
                key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              tags:
                - tag: component
                  value: system
                - tag: source
                  value: official-api
            - uuid: 998c2ccbe48144809c7f907d5439dfc4
              name: 'Official load average 5m on {#UNIFI.DEVICE.NAME}'
              type: DEPENDENT
              key: 'unifi.official.system.loadavg_5[{#UNIFI.DEVICE.ID}]'
              history: 90d
              value_type: FLOAT
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - $.loadAverage5Min
              master_item:
                key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              tags:
                - tag: component
                  value: system
                - tag: source
                  value: official-api
            - uuid: c19f4b566cb841afa9d7ce11403ca5fd
              name: 'Official load average 15m on {#UNIFI.DEVICE.NAME}'
              type: DEPENDENT
              key: 'unifi.official.system.loadavg_15[{#UNIFI.DEVICE.ID}]'
              history: 90d
              value_type: FLOAT
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - $.loadAverage15Min
              master_item:
                key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              tags:
                - tag: component
                  value: system
                - tag: source
                  value: official-api
            - uuid: 77427d98f7ce44cd9984012ff23ea8f6
              name: 'Official uptime on {#UNIFI.DEVICE.NAME}'
              type: DEPENDENT
              key: 'unifi.official.system.uptime[{#UNIFI.DEVICE.ID}]'
              history: 90d
              units: uptime
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - $.uptimeSec
              master_item:
                key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              tags:
                - tag: component
                  value: system
                - tag: source
                  value: official-api
            - uuid: 9d7eb672d6fd43ccb883c5c78f06420e
              name: 'Official uplink download rate on {#UNIFI.DEVICE.NAME}'
              type: DEPENDENT
              key: 'unifi.official.uplink.rx_bps[{#UNIFI.DEVICE.ID}]'
              history: 90d
              value_type: FLOAT
              units: bps
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - $.uplink.rxRateBps
                  error_handler: CUSTOM_VALUE
                  error_handler_params: '0'
              master_item:
                key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              tags:
                - tag: component
                  value: internet
                - tag: source
                  value: official-api
            - uuid: 996cec1b652b4068a457a3d2c931f487
              name: 'Official uplink upload rate on {#UNIFI.DEVICE.NAME}'
              type: DEPENDENT
              key: 'unifi.official.uplink.tx_bps[{#UNIFI.DEVICE.ID}]'
              history: 90d
              value_type: FLOAT
              units: bps
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - $.uplink.txRateBps
                  error_handler: CUSTOM_VALUE
                  error_handler_params: '0'
              master_item:
                key: 'unifi_udm_pro_api.py["device-stats","{$UNIFI.API.URL}","{$UNIFI.API.KEY}","{$UNIFI.SITE.ID}","{#UNIFI.DEVICE.ID}","{$UNIFI.TLS.ARG}"]'
              tags:
                - tag: component
                  value: internet
                - tag: source
                  value: official-api
          graph_prototypes:
            - uuid: 49184ab29ea9448e9fa347f67e85d668
              name: 'Official system health on {#UNIFI.DEVICE.NAME}'
              graph_items:
                - color: FF7043
                  item:
                    host: 'UniFi UDM Pro API Monitoring'
                    key: 'unifi.official.system.cpu.percent[{#UNIFI.DEVICE.ID}]'
                - sortorder: '1'
                  color: 7E57C2
                  item:
                    host: 'UniFi UDM Pro API Monitoring'
                    key: 'unifi.official.system.memory.percent[{#UNIFI.DEVICE.ID}]'
          timeout: 60s
'''

TLS_MACRO = '''        - macro: '{$UNIFI.TLS.ARG}'
          value: '--timeout=20'
          description: 'Collector TLS argument. Keep --timeout=20 for compatibility with self-signed consoles, or set --verify-tls to validate the HTTPS certificate.'
'''

STATS_FILTER_MACRO = '''        - macro: '{$UNIFI.LLD.OFFICIAL.STATS.MODEL.MATCHES}'
          value: '(?i)^(UDM.*|UCG.*|UXG.*)$'
          description: 'Gateway model regex included in official Integration API statistics/latest discovery.'
'''

KEY_PATTERN = re.compile(r"unifi_udm_pro_api\.py\[(.*?)\]")


def add_tls_arg(match):
    inside = match.group(1)
    if "{$UNIFI.TLS.ARG}" in inside:
        return match.group(0)
    return 'unifi_udm_pro_api.py[' + inside + ',"{$UNIFI.TLS.ARG}"]'


for version in ("7.0", "8.0"):
    path = ROOT / version / f"UniFi_UDM_Pro_API_Monitoring_{version}.yaml"
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, "version: 0.6-10", "version: 0.7-0", f"{version} vendor version")
    text = text.replace(
        "Local UniFi Network API key generated in Control Plane > Integrations.",
        "Local UniFi Network API key generated in UniFi Network > Integrations.",
    )

    # Add the TLS option macro to every collector invocation and every exact
    # master/trigger reference to those keys.
    text = KEY_PATTERN.sub(add_tls_arg, text)

    if "macro: '{$UNIFI.TLS.ARG}'" not in text:
        text = replace_once(
            text,
            "        - macro: '{$UNIFI.CPU.WARN}'\n",
            TLS_MACRO + "        - macro: '{$UNIFI.CPU.WARN}'\n",
            f"{version} TLS macro anchor",
        )
    if "macro: '{$UNIFI.LLD.OFFICIAL.STATS.MODEL.MATCHES}'" not in text:
        text = replace_once(
            text,
            "        - macro: '{$UNIFI.LLD.CLIENT.TYPE.MATCHES}'\n",
            STATS_FILTER_MACRO + "        - macro: '{$UNIFI.LLD.CLIENT.TYPE.MATCHES}'\n",
            f"{version} official stats filter macro anchor",
        )
    if "UniFi official gateway statistics discovery" not in text:
        text = replace_once(
            text,
            "      discovery_rules:\n",
            "      discovery_rules:\n" + OFFICIAL_RULE,
            f"{version} discovery rules anchor",
        )

    old_desc = '''        Template for monitoring a Ubiquiti UniFi Dream Machine Pro through the
        local UniFi Network API.
        
        Requires the external script unifi_udm_pro_api.py in the Zabbix server
        or proxy external scripts directory.
'''
    new_desc = '''        Template for monitoring a Ubiquiti UniFi Dream Machine Pro through the
        local UniFi Network API. Version 0.7.0 adds parallel collection from the
        documented Integration API statistics/latest endpoint for Network 10.6
        validation while retaining existing legacy telemetry for compatibility.
        
        Requires the external script unifi_udm_pro_api.py in the Zabbix server
        or proxy external scripts directory.
'''
    if old_desc in text:
        text = text.replace(old_desc, new_desc, 1)

    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# English README.
# ---------------------------------------------------------------------------
en_path = ROOT / "README.md"
en = en_path.read_text(encoding="utf-8").replace("0.6.10", "0.7.0")
en = replace_once(
    en,
    "Zabbix template project for monitoring a Ubiquiti UniFi Dream Machine Pro\nthrough the UniFi Network API, Site Manager API, CEF/syslog events, and\noptional NetFlow/IPFIX data.\n",
    "Zabbix template project for monitoring a Ubiquiti UniFi Dream Machine Pro\nprimarily through the local UniFi Network APIs. The current collector implements\nthe official Integration API and keeps selected legacy Network endpoints for\noperational metrics that have not yet been migrated. Site Manager, CEF/syslog,\nand NetFlow/IPFIX remain planned integrations.\n",
    "English README intro",
)
en = en.replace(
    "- Use UniFi logs and CEF exports for operational and security events.\n",
    "- Gradually migrate advanced telemetry from legacy Network endpoints to the documented Integration API.\n",
)
en_api = '''## Data Sources

### Currently Implemented

- Official local Network Integration API: `https://<udm-pro>/proxy/network/integration/v1`
- Legacy Network operational endpoint used for advanced telemetry not yet
  available in equivalent form through the Integration API:
  `/proxy/network/api/s/<site>/stat/device`

### Planned

- Site Manager API: `https://api.ui.com/v1`
- UniFi System Logs / SIEM CEF export
- Traffic Flows / NetFlow/IPFIX

Site Manager, CEF/syslog, and NetFlow/IPFIX are roadmap items and are not
currently collected by the template.

## Creating the Local UniFi Network API Key

The current template uses the **local UniFi Network API key**. This is separate
from a Site Manager API key.

### UniFi Network 10.6.x

Current Ubiquiti guidance places local Network API key management and the
version-specific API documentation under **UniFi Network > Integrations**.

Official reference: [Getting Started with the Official UniFi API](https://help.ui.com/hc/en-us/articles/30076656117655-Getting-Started-with-the-Official-UniFi-API).

Recommended process:

1. Sign in to the UniFi Console/UDM Pro with an account allowed to administer Network.
2. Open **UniFi Network**.
3. Open **Integrations**.
4. Create a local Network API key.
5. Give it a clear name such as `zabbix-udm-pro-monitoring`.
6. Copy and store the generated key securely.
7. Store it in the Zabbix secret macro `{$UNIFI.API.KEY}`.

> The local Network API key is not the same credential as a Site Manager API
> key for `api.ui.com`.

The collector uses the local API at:

```text
https://<udm-pro-ip>/proxy/network/integration/v1
```

The **Integrations** page also exposes API documentation matching the installed
Network version. Review it after Network upgrades because endpoint schemas can
change between releases.

### Test the Key

```bash
curl --fail-with-body -sS -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/info"

curl --fail-with-body -sS -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/sites"
```

After obtaining the site ID, test devices and the documented latest statistics
endpoint:

```bash
curl --fail-with-body -sS -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/sites/<site-id>/devices"

curl --fail-with-body -sS -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/sites/<site-id>/devices/<device-id>/statistics/latest"
```

The latest statistics endpoint is used in 0.7.0 in parallel with the existing
legacy telemetry. It supplies documented fields such as uptime, CPU and memory
utilization, load averages, and uplink RX/TX rates.

### Common Errors

- `401 Unauthorized`: invalid/missing key or a key from the wrong UniFi API surface.
- `403 Forbidden`: the associated key/account cannot access the requested resource.
- Timeout/connection errors: check routing, firewall, DNS, and HTTPS reachability.
- TLS errors: use a trusted certificate and enable verification when possible.

### Site Manager API Key — Planned

Site Manager uses a different key and `https://api.ui.com/v1`. Site Manager
support remains planned and is not required by the current template.

'''
a = en.index("## Planned Sources")
b = en.index("### Security Recommendations")
en = en[:a] + en_api + en[b:]
en = en.replace(
    "- Prefer HTTPS with valid certificates where possible. If the UDM Pro uses a\n  self-signed certificate, testing with `curl -k` is acceptable on a trusted LAN,\n  but production scripts should make this behavior explicit and documented.\n",
    "- Prefer HTTPS with valid certificates where possible. `{$UNIFI.TLS.ARG}` defaults\n  to `--timeout=20`, preserving the current self-signed-certificate behavior. Set\n  it to `--verify-tls` after the console certificate is trusted by the Zabbix host.\n",
)
en_components = '''## Zabbix Components

- Low-level discovery for devices, clients, networks, WAN links, interfaces,
  storage, radios, and PoE budgets.
- External master items and dependent items for local UniFi Network APIs.
- Parallel official `statistics/latest` collection for gateway-class devices.
- Existing legacy Network telemetry retained for WAN, storage, PoE, radio, and
  other fields without a fully equivalent official replacement yet.
- Site Manager, CEF/syslog, and NetFlow/IPFIX remain planned integrations.

'''
a = en.index("## Planned Zabbix Components")
b = en.index("## Zabbix Template")
en = en[:a] + en_components + en[b:]
en = en.replace(
    "- System health from `/proxy/network/api/s/default/stat/device`: CPU, memory,\n",
    "- Parallel official Integration API device statistics: CPU, memory, uptime,\n  1/5/15-minute load averages, and uplink RX/TX rates for selected gateway models.\n- System health from `/proxy/network/api/s/default/stat/device`: CPU, memory,\n",
    1,
)
en = en.replace("{$UNIFI.CPU.WARN}\n", "{$UNIFI.TLS.ARG}\n{$UNIFI.CPU.WARN}\n", 1)
en = en.replace(
    "### Suggested Next Additions\n\n### API Review Notes",
    "### Suggested Next Additions\n\n"
    "- Continue migrating WAN, storage, PoE, and radio telemetry to documented API endpoints when equivalent fields are available.\n"
    "- Validate Network 10.6.x payloads on additional gateway models and refine `{$UNIFI.LLD.OFFICIAL.STATS.MODEL.MATCHES}` as needed.\n"
    "- Add Site Manager, CEF/syslog, and NetFlow/IPFIX as separate optional integrations.\n\n"
    "### API Review Notes",
)
en = en.replace(
    "## Confirmed Local API Responses\n\n",
    "## Confirmed Local API Responses from Previous Validation\n\n"
    "The examples below document an earlier validation environment and are retained\n"
    "for regression reference. Use the Network 10.6.x instructions above for current\n"
    "API-key creation and compatibility validation.\n\n",
    1,
)
en_path.write_text(en, encoding="utf-8")


# ---------------------------------------------------------------------------
# Portuguese README.
# ---------------------------------------------------------------------------
pt_path = ROOT / "README.pt-BR.md"
pt = pt_path.read_text(encoding="utf-8").replace("0.6.10", "0.7.0")
pt = replace_once(
    pt,
    "Projeto de template Zabbix para monitorar um Ubiquiti UniFi Dream Machine Pro\npela API do UniFi Network, API do Site Manager, eventos CEF/syslog e dados\nopcionais de NetFlow/IPFIX.\n",
    "Projeto de template Zabbix para monitorar um Ubiquiti UniFi Dream Machine Pro\nprincipalmente pelas APIs locais do UniFi Network. O coletor atual implementa a\nIntegration API oficial e mantém endpoints legados selecionados para métricas\noperacionais ainda não migradas. Site Manager, CEF/syslog e NetFlow/IPFIX\npermanecem como integrações planejadas.\n",
    "Portuguese README intro",
)
pt = pt.replace(
    "- Usar logs UniFi e exportações CEF para eventos operacionais e de segurança.\n",
    "- Migrar gradualmente telemetria avançada dos endpoints legados para a Integration API documentada.\n",
)
pt_api = '''## Fontes de Dados

### Implementadas Atualmente

- Integration API local oficial do UniFi Network:
  `https://<udm-pro>/proxy/network/integration/v1`
- Endpoint operacional legado do Network usado para telemetria avançada ainda
  sem equivalente completo na Integration API:
  `/proxy/network/api/s/<site>/stat/device`

### Planejadas

- API do UniFi Site Manager: `https://api.ui.com/v1`
- Logs do sistema UniFi / exportação SIEM CEF
- Fluxos de tráfego / NetFlow/IPFIX

Site Manager, CEF/syslog e NetFlow/IPFIX são itens de roadmap e ainda não são
coletados pelo template atual.

## Criação da Chave da API Local do UniFi Network

O template atual utiliza a **chave da API local do UniFi Network**. Ela é uma
credencial diferente da chave da API do Site Manager.

### UniFi Network 10.6.x

A orientação oficial atual da Ubiquiti coloca a criação da chave da API local e
a documentação específica da versão em **UniFi Network > Integrations**.

Referência oficial: [Getting Started with the Official UniFi API](https://help.ui.com/hc/en-us/articles/30076656117655-Getting-Started-with-the-Official-UniFi-API).

Processo recomendado:

1. Acesse o UniFi Console/UDM Pro com uma conta que possa administrar o Network.
2. Abra **UniFi Network**.
3. Abra **Integrations**.
4. Crie uma chave da API local do Network.
5. Use um nome claro, como `zabbix-udm-pro-monitoring`.
6. Copie e armazene a chave gerada com segurança.
7. No Zabbix, grave-a na macro secreta `{$UNIFI.API.KEY}`.

> A chave local do UniFi Network não é a mesma chave utilizada pelo Site Manager
> em `api.ui.com`.

O coletor utiliza a API local em:

```text
https://<udm-pro-ip>/proxy/network/integration/v1
```

A tela **Integrations** também disponibiliza a documentação da API correspondente
à versão instalada do Network. Revise-a após upgrades, pois schemas e endpoints
podem mudar entre versões.

### Testando a Chave

```bash
curl --fail-with-body -sS -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/info"

curl --fail-with-body -sS -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/sites"
```

Depois de obter o site ID, teste dispositivos e o endpoint documentado de
estatísticas mais recentes:

```bash
curl --fail-with-body -sS -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/sites/<site-id>/devices"

curl --fail-with-body -sS -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/sites/<site-id>/devices/<device-id>/statistics/latest"
```

Na versão 0.7.0, esse endpoint é coletado em paralelo com a telemetria legada e
fornece campos documentados como uptime, CPU, memória, load averages e taxas
RX/TX do uplink.

### Erros Comuns

- `401 Unauthorized`: chave inválida/ausente ou chave de outra superfície da API UniFi.
- `403 Forbidden`: a chave/conta associada não possui acesso ao recurso.
- Timeout/erro de conexão: verifique roteamento, firewall, DNS e HTTPS.
- Erro TLS: use certificado confiável e habilite a validação quando possível.

### Chave da API do Site Manager — Planejada

O Site Manager usa uma chave diferente e `https://api.ui.com/v1`. Esse suporte
continua planejado e não é necessário para o funcionamento atual do template.

'''
a = pt.index("## Fontes Planejadas")
b = pt.index("### Recomendações de Segurança")
pt = pt[:a] + pt_api + pt[b:]
pt = pt.replace(
    "- Prefira HTTPS com certificados válidos sempre que possível. Se o UDM Pro usar\n  certificado autoassinado, testar com `curl -k` é aceitável em uma LAN\n  confiável, mas esse comportamento deve ficar explícito e documentado nos\n  scripts de produção.\n",
    "- Prefira HTTPS com certificados válidos sempre que possível. `{$UNIFI.TLS.ARG}`\n  usa `--timeout=20` por padrão, preservando compatibilidade com consoles de\n  certificado autoassinado. Troque para `--verify-tls` quando o certificado do\n  console for confiável para o servidor/proxy Zabbix.\n",
)
pt_components = '''## Componentes Zabbix

- Descoberta de baixo nível para dispositivos, clientes, redes, WANs, interfaces,
  storage, rádios e orçamento PoE.
- External checks mestres e itens dependentes para as APIs locais do Network.
- Coleta oficial paralela de `statistics/latest` para dispositivos gateway.
- Telemetria legada existente mantida para WAN, storage, PoE, rádio e outros
  campos ainda sem substituto oficial completamente equivalente.
- Site Manager, CEF/syslog e NetFlow/IPFIX permanecem integrações planejadas.

'''
a = pt.index("## Componentes Zabbix Planejados")
b = pt.index("## Template Zabbix")
pt = pt[:a] + pt_components + pt[b:]
pt = pt.replace(
    "- Saúde do sistema via `/proxy/network/api/s/default/stat/device`: CPU, memória,\n",
    "- Estatísticas paralelas pela Integration API oficial: CPU, memória, uptime,\n  load averages de 1/5/15 minutos e taxas RX/TX do uplink para gateways selecionados.\n- Saúde do sistema via `/proxy/network/api/s/default/stat/device`: CPU, memória,\n",
    1,
)
pt = pt.replace("{$UNIFI.CPU.WARN}\n", "{$UNIFI.TLS.ARG}\n{$UNIFI.CPU.WARN}\n", 1)
pt = pt.replace(
    "### Próximas Adições Sugeridas\n\n### Notas de Revisão da API",
    "### Próximas Adições Sugeridas\n\n"
    "- Continuar migrando WAN, storage, PoE e rádio para endpoints documentados quando houver equivalência funcional.\n"
    "- Validar os payloads 10.6.x em outros modelos de gateway e ajustar `{$UNIFI.LLD.OFFICIAL.STATS.MODEL.MATCHES}` quando necessário.\n"
    "- Implementar Site Manager, CEF/syslog e NetFlow/IPFIX como integrações opcionais separadas.\n\n"
    "### Notas de Revisão da API",
)
pt = pt.replace(
    "## Respostas Locais da API Confirmadas\n\n",
    "## Respostas Locais da API Confirmadas em Validação Anterior\n\n"
    "Os exemplos abaixo registram um ambiente de validação anterior e foram mantidos\n"
    "como referência de regressão. Para criação de chave e compatibilidade atual, siga\n"
    "a seção **UniFi Network 10.6.x** acima.\n\n",
    1,
)
pt_path.write_text(pt, encoding="utf-8")


# ---------------------------------------------------------------------------
# Changelogs.
# ---------------------------------------------------------------------------
changelog_en = ROOT / "CHANGELOG.md"
ce = changelog_en.read_text(encoding="utf-8")
section_en = '''## 0.7.0 - Unreleased

### Added

- Added the `device-stats` collector command for the documented Integration API
  `/sites/{siteId}/devices/{deviceId}/statistics/latest` endpoint.
- Added parallel official gateway statistics discovery to both Zabbix 7.0 and
  8.0 templates with CPU, memory, 1/5/15-minute load averages, uptime, and
  uplink RX/TX rate items.
- Added official statistics collector health and last-error item prototypes.
- Added `{$UNIFI.LLD.OFFICIAL.STATS.MODEL.MATCHES}` to control which gateway
  models use the parallel official statistics collection.
- Added `{$UNIFI.TLS.ARG}`. Keep `--timeout=20` for current self-signed
  compatibility or set it to `--verify-tls` to enable certificate validation
  for all external checks.

### Changed

- Updated both template vendor versions to `0.7-0` and collector version to
  `0.7.0`.
- Updated the API key macro description and bilingual documentation for UniFi
  Network 10.6.x using **UniFi Network > Integrations**.
- Clarified implemented local API sources versus planned Site Manager, CEF/syslog,
  and NetFlow/IPFIX integrations.
- Kept existing legacy telemetry and dashboards unchanged while official
  statistics are validated in parallel.

'''
ce = replace_once(ce, "## 0.6.10 - Unreleased\n", section_en + "## 0.6.10 - Unreleased\n", "English changelog")
changelog_en.write_text(ce, encoding="utf-8")

changelog_pt = ROOT / "CHANGELOG.pt-BR.md"
cp = changelog_pt.read_text(encoding="utf-8")
section_pt = '''## 0.7.0 - Não Lançado

### Adicionado

- Adicionado o comando `device-stats` ao coletor para o endpoint documentado da
  Integration API `/sites/{siteId}/devices/{deviceId}/statistics/latest`.
- Adicionada coleta oficial paralela de estatísticas de gateway aos templates
  Zabbix 7.0 e 8.0, com CPU, memória, load averages de 1/5/15 minutos, uptime e
  taxas RX/TX do uplink.
- Adicionados protótipos de saúde e último erro da coleta oficial de estatísticas.
- Adicionada `{$UNIFI.LLD.OFFICIAL.STATS.MODEL.MATCHES}` para controlar quais
  modelos de gateway usam a coleta oficial paralela.
- Adicionada `{$UNIFI.TLS.ARG}`. Mantenha `--timeout=20` para compatibilidade
  atual com certificados autoassinados ou altere para `--verify-tls` para ativar
  validação do certificado em todos os external checks.

### Alterado

- Atualizadas as versões de vendor dos dois templates para `0.7-0` e a versão
  do coletor para `0.7.0`.
- Atualizada a descrição da macro da chave e a documentação bilíngue para UniFi
  Network 10.6.x usando **UniFi Network > Integrations**.
- Separadas claramente as fontes locais já implementadas das integrações
  planejadas de Site Manager, CEF/syslog e NetFlow/IPFIX.
- Mantidas as métricas legadas e dashboards atuais enquanto as estatísticas
  oficiais são validadas em paralelo.

'''
cp = replace_once(cp, "## 0.6.10 - Não Lançado\n", section_pt + "## 0.6.10 - Não Lançado\n", "Portuguese changelog")
changelog_pt.write_text(cp, encoding="utf-8")


# ---------------------------------------------------------------------------
# Validation guide.
# ---------------------------------------------------------------------------
validation = '''# Validation Checklist

Use this checklist before promoting the template to production. Version 0.7.0
adds parallel validation of the documented UniFi Network Integration API device
statistics endpoint while keeping legacy telemetry in place.

## 1. Script Sanity

```bash
python3 -m py_compile unifi_udm_pro_api.py
```

## 2. Integration API Reachability

```bash
python3 unifi_udm_pro_api.py info "$UNIFI_API_URL" "$UNIFI_API_KEY"
python3 unifi_udm_pro_api.py sites "$UNIFI_API_URL" "$UNIFI_API_KEY"
```

Expected: valid JSON payloads without an `error` field.

## 3. Official Device Statistics

First identify the site ID and gateway device ID, then test:

```bash
python3 unifi_udm_pro_api.py devices "$UNIFI_API_URL" "$UNIFI_API_KEY" "$UNIFI_SITE_ID"
python3 unifi_udm_pro_api.py device-stats "$UNIFI_API_URL" "$UNIFI_API_KEY" "$UNIFI_SITE_ID" "$UNIFI_GATEWAY_DEVICE_ID"
```

Expected fields on Network versions supporting the documented endpoint include
`uptimeSec`, `cpuUtilizationPct`, `memoryUtilizationPct`, load averages, and
`uplink.rxRateBps` / `uplink.txRateBps`.

## 4. TLS Validation

The templates define `{$UNIFI.TLS.ARG}`.

- Default `--timeout=20`: preserves existing behavior, including self-signed
  console certificates.
- Set to `--verify-tls`: the collector validates the HTTPS certificate using the
  Zabbix server/proxy system trust store.

After enabling verification, confirm both Integration API and legacy collector
health items remain available.

## 5. Legacy Network API Payloads

```bash
python3 unifi_udm_pro_api.py system-health "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py gateway-info "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py wan-health "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py network-services "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py poe-budget "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py radio-performance "$UNIFI_API_URL" "$UNIFI_API_KEY" default
python3 unifi_udm_pro_api.py port-telemetry "$UNIFI_API_URL" "$UNIFI_API_KEY" default
```

Expected: valid JSON payloads; numeric fields should be numeric.

## 6. Zabbix Template Checks

1. Import `7.0/UniFi_UDM_Pro_API_Monitoring_7.0.yaml` for Zabbix 7.0 or
   `8.0/UniFi_UDM_Pro_API_Monitoring_8.0.yaml` for Zabbix 8.0.
2. Link the template to a test UDM Pro host.
3. Set `{$UNIFI.API.URL}`, `{$UNIFI.API.KEY}`, `{$UNIFI.SITE.ID}` when needed,
   and `{$UNIFI.NETWORK.SITE}`.
4. Confirm the official gateway statistics discovery selects the expected device.
5. Confirm official CPU, memory, load, uptime, and uplink items receive data.
6. Confirm legacy collector status items remain `1` and existing dashboards keep data.
7. Confirm no dependent item is unsupported after the first collection cycles.

## 7. Trigger Validation

1. Confirm the official statistics collection trigger stays recovered.
2. Confirm informational firmware/reboot triggers stay stable.
3. Confirm WAN/radio/PoE threshold triggers recover after values normalize.
4. Confirm `gateway-info` dependent items (`name`, `type`, `mac`, `model`, `version`) are populated.
'''
(ROOT / "docs" / "VALIDATION.md").write_text(validation, encoding="utf-8")

print("UniFi Network 10.6 / template 0.7.0 transformation completed")
