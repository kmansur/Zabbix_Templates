# Monitoramento UniFi UDM Pro para Zabbix

Monitoramento unificado do UniFi Network para Zabbix 7.0 e 8.0.

Versão: **0.8.0**  
Autor: **Karim Mansur / Net Tech**

## O que instalar

A versão 0.8 usa um único template e um único coletor externo. Não existe mais template complementar de dashboard nem um segundo script de telemetria.

```text
UniFi UDM Pro API Monitoring/
├── 7.0/UniFi_UDM_Pro_API_Monitoring_7.0.yaml
├── 8.0/UniFi_UDM_Pro_API_Monitoring_8.0.yaml
└── unifi_udm_pro_api.py
```

Escolha o YAML correspondente à versão principal do Zabbix e instale `unifi_udm_pro_api.py` no diretório `ExternalScripts`.

Exemplo no Debian:

```bash
install -o root -g zabbix -m 0750 \
  unifi_udm_pro_api.py \
  /usr/lib/zabbix/externalscripts/unifi_udm_pro_api.py
```

Depois importe o template e vincule-o ao host UniFi.

## Chave de API do UniFi

Crie uma chave local em **UniFi Network > Integrations**. A URL base local validada é:

```text
https://<gateway>/proxy/network/integration/v1
```

O coletor também usa endpoints locais do Network para telemetria operacional que ainda não é exposta pela Integration API.

## Macros necessárias

Configure no template/host conforme o controlador:

```text
{$UNIFI.API.URL}
{$UNIFI.API.KEY}
{$UNIFI.SITE.ID}
{$UNIFI.NETWORK.SITE}
{$UNIFI.TLS.ARG}
```

`{$UNIFI.SITE.ID}` é o UUID do site da Integration API quando exigido pelos endpoints documentados. `{$UNIFI.NETWORK.SITE}` é a referência interna do site do Network, normalmente `default` em um UDM com site único.

`{$UNIFI.TLS.ARG}` usa por padrão `--timeout=20`. Use `--verify-tls` quando o certificado do gateway for confiável pelo servidor Zabbix.

## Telemetria do dashboard

O template principal já inclui os contratos utilizados pelo `Zabbix-UniFi-Dashboard`.

Janelas móveis de tráfego:

| Período do dashboard | Janela | Intervalo de coleta |
|---|---:|---:|
| 1h | 3600 s | 2m |
| 1D | 86400 s | 5m |
| 1S | 604800 s | 15m |
| 1M | 2592000 s (30 dias) | 1h |

Ranking de clientes:

```text
unifi.client.traffic.bytes[1h,<id>]
unifi.client.traffic.bytes[1d,<id>]
unifi.client.traffic.bytes[1w,<id>]
unifi.client.traffic.bytes[1m,<id>]
```

Ranking DPI:

```text
unifi.dpi.app.bytes[1h,<id>]
unifi.dpi.app.bytes[1d,<id>]
unifi.dpi.app.bytes[1w,<id>]
unifi.dpi.app.bytes[1m,<id>]
```

Sinal atual dos clientes Wi-Fi e conectividade:

```text
unifi.radio.rssi[<client-id>]
unifi.wifi.association.success
unifi.wifi.authentication.success
unifi.wifi.dhcp.success
unifi.wifi.dns.success
```

## Comandos do coletor unificado

O coletor mantém os comandos já existentes na versão 0.7 e acrescenta:

```bash
./unifi_udm_pro_api.py version
./unifi_udm_pro_api.py dashboard-client-status URL API_KEY default --timeout=20
./unifi_udm_pro_api.py dashboard-traffic URL API_KEY default 3600 --timeout=20
./unifi_udm_pro_api.py dpi-catalog URL API_KEY default --timeout=20
./unifi_udm_pro_api.py wifi-connectivity URL API_KEY default --timeout=20
```

`dashboard-traffic` retorna o tráfego por cliente e por aplicação DPI usando uma única consulta v2 para a janela selecionada.

## APIs utilizadas

- Integration API: `/proxy/network/integration/v1`
- API operacional legada: `/proxy/network/api/s/<site>/...`
- Tráfego: `/proxy/network/v2/api/site/<site>/traffic`
- Conectividade Wi-Fi: `/proxy/network/v2/api/site/<site>/wifi-connectivity`

No UniFi Network 10.6.101, os parâmetros `start` e `end` do endpoint de tráfego precisam estar em **milissegundos Unix epoch**.

Os IDs das aplicações DPI usam a composição `(category << 16) + application`; os nomes são resolvidos pelo catálogo DPI da Integration API.

## Validação

A validação real foi feita com UniFi Network **10.6.101**, UniFi OS **5.1.31** e Zabbix **8.0.0beta2**.

Janelas validadas e tempos aproximados observados no controlador:

- 1h: funcionando
- 1D: funcionando
- 1S: ~0,74 s
- 30 dias: ~1,00 s

Também foram validados RSSI atual dos clientes, catálogo DPI com 2.112 aplicações e as métricas de associação, autenticação, DHCP e DNS do Wi-Fi.

Consulte `docs/DASHBOARD_TELEMETRY.md` e `docs/VALIDATION.md` para mais detalhes.
