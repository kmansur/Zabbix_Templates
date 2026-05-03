# Monitoramento UniFi UDM Pro via API

Versão em inglês: [README.md](README.md)

> Status de desenvolvimento: este template ainda está em desenvolvimento ativo
> e deve ser validado em um host de teste antes do uso em produção.
>
> Manutenção da documentação: quando o `README.md` em inglês for atualizado,
> atualize este `README.pt-BR.md` na mesma alteração.

Projeto de template Zabbix para monitorar um Ubiquiti UniFi Dream Machine Pro
pela API do UniFi Network, API do Site Manager, eventos CEF/syslog e dados
opcionais de NetFlow/IPFIX.

## Objetivos

- Descobrir sites, dispositivos, redes, clientes, links WAN e dados do gateway UniFi.
- Coletar saúde do gateway, latência WAN, perda de pacotes, uptime, tráfego e estado dos dispositivos.
- Usar logs UniFi e exportações CEF para eventos operacionais e de segurança.
- Manter SNMP como fallback opcional para contadores básicos de interfaces.

## Fontes Planejadas

- API local do Network: `https://<udm-pro>/proxy/network/integration/v1`
- API do Site Manager: `https://api.ui.com/v1`
- Logs do sistema UniFi / exportação SIEM CEF
- Fluxos de tráfego / NetFlow/IPFIX

## Criação das Chaves de API

Este projeto pode usar duas chaves de API diferentes. A chave local do UniFi
Network é a principal para monitorar um UDM Pro na LAN. A chave da API do Site
Manager é opcional e serve para dados em nuvem ou multi-site vindos de
`api.ui.com`.

### Chave da API Local do UniFi Network

Use esta chave para acesso direto ao UDM Pro, por exemplo:

```text
https://<udm-pro-ip>/proxy/network/integration/v1
```

Processo recomendado:

1. Acesse a interface web do UDM Pro com uma conta administradora.
2. Abra a aplicação UniFi Network.
3. Vá em **Settings**.
4. Abra **Control Plane**.
5. Abra **Integrations**.
6. Localize a seção **API Keys** ou **Network API**.
7. Crie uma nova chave de API.
8. Use um nome claro para a chave, por exemplo:

   ```text
   zabbix-udm-pro-monitoring
   ```

9. Se o UniFi oferecer expiração, escolha a política adequada ao seu ambiente.
   Para produção, uma chave sem expiração é prática, mas uma política de rotação
   é mais segura.
10. Copie a chave gerada imediatamente e armazene-a em uma macro secreta do
    Zabbix ou no ambiente do script. O UniFi pode não exibir a chave completa
    novamente.
11. Teste a chave a partir do servidor ou proxy Zabbix:

    ```bash
    curl -k \
      -H "Accept: application/json" \
      -H "X-API-KEY: <api-key>" \
      "https://<udm-pro-ip>/proxy/network/integration/v1/sites"
    ```

Resultado esperado: uma resposta JSON com o site ou os sites UniFi disponíveis.
Em uma instalação típica com UDM Pro, normalmente existe apenas um site.

Depois de listar os sites, use o ID retornado para testar dispositivos:

```bash
curl -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/sites/<site-id>/devices"
```

E clientes:

```bash
curl -k \
  -H "Accept: application/json" \
  -H "X-API-KEY: <api-key>" \
  "https://<udm-pro-ip>/proxy/network/integration/v1/sites/<site-id>/clients"
```

### Chave da API do Site Manager

Use esta chave apenas quando o template precisar de dados em nuvem do UniFi Site
Manager, como inventário multi-site ou métricas de ISP em:

```text
https://api.ui.com/v1
```

Processo recomendado:

1. Acesse a área de desenvolvedor ou de API do Site Manager associada à sua
   conta UI.
2. Crie uma chave de API para a conta que administra o UDM Pro.
3. Use um nome claro para a chave, por exemplo:

   ```text
   zabbix-unifi-site-manager
   ```

4. Copie a chave imediatamente e armazene-a com segurança.
5. Teste a chave:

   ```bash
   curl \
     -H "Accept: application/json" \
     -H "X-API-Key: <api-key>" \
     "https://api.ui.com/v1/sites"
   ```

6. Teste métricas de ISP se você pretende usar histórico WAN do Site Manager:

   ```bash
   curl \
     -H "Accept: application/json" \
     -H "X-API-Key: <api-key>" \
     "https://api.ui.com/ea/isp-metrics/5m?duration=24h"
   ```

### Recomendações de Segurança

- Crie uma conta dedicada de administração ou serviço para monitoramento quando possível.
- Conceda apenas as permissões mínimas necessárias para monitoramento somente leitura.
- Nunca grave chaves de API diretamente em scripts, templates ou arquivos versionados no Git.
- Armazene a chave local em uma macro secreta do Zabbix, por exemplo:

  ```text
  {$UNIFI.API.KEY}
  ```

- Armazene a URL do UDM Pro em uma macro comum, por exemplo:

  ```text
  {$UNIFI.API.URL}
  ```

- Restrinja o acesso à API no firewall para que apenas o servidor ou proxy Zabbix
  consiga acessar a interface de gerenciamento do UDM Pro.
- Prefira HTTPS com certificados válidos sempre que possível. Se o UDM Pro usar
  certificado autoassinado, testar com `curl -k` é aceitável em uma LAN
  confiável, mas esse comportamento deve ficar explícito e documentado nos
  scripts de produção.
- Rotacione a chave após mudanças de equipe, suspeita de exposição ou vazamento
  em repositório.
- Revogue chaves antigas que não são mais usadas.

## Componentes Zabbix Planejados

- Descoberta de baixo nível para dispositivos, clientes, redes, links WAN e interfaces.
- Itens HTTP/API para métricas do UniFi Network e Site Manager.
- Itens dependentes para parsing de JSON.
- Protótipos de trigger para degradação WAN, dispositivo offline, perda de pacote,
  alta latência, atualização de firmware e eventos de segurança.
- Itens trapper syslog opcionais para eventos CEF.

## Template Zabbix

Versão atual do projeto:

```text
0.6.4
```

O template importável para Zabbix 7.0 é:

```text
UniFi UDM Pro API Monitoring.yaml
```

Antes de importar ou habilitar o template:

1. Instale `unifi_udm_pro_api.py` no servidor ou proxy Zabbix.
2. Importe `UniFi UDM Pro API Monitoring.yaml`.
3. Vincule o template ao host do UDM Pro.
4. Configure as macros do host:

   ```text
   {$UNIFI.API.URL} = https://xxx.xxx.xxx.xxx
   {$UNIFI.API.KEY} = sua chave local da API UniFi Network
   {$UNIFI.SITE.ID} = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   {$UNIFI.NETWORK.SITE} = default
   ```

`{$UNIFI.API.URL}` pode ser a URL raiz do UDM Pro
(`https://xxx.xxx.xxx.xxx`) ou o prefixo completo da Integration API
(`https://xxx.xxx.xxx.xxx/proxy/network/integration/v1`). O script normaliza o
valor corretamente tanto para chamadas da Integration API quanto para chamadas
da Network API.

`{$UNIFI.SITE.ID}` pode ficar vazio quando o controller possui apenas um site.
O script descobrirá o site automaticamente. Itens fixos de sistema e WAN selecionam automaticamente o dispositivo UDM a partir do payload da Network API. Não
defina uma macro de device ID para uso normal do template; IDs explícitos de
dispositivo da Network API são necessários apenas para testes manuais do script.

O template inicial inclui:

- Versão da aplicação UniFi Network.
- Resumo de dispositivos: total, online, offline e atualizações de firmware disponíveis.
- Resumo de clientes: total, cabeados e sem fio.
- Resumo de redes: total, habilitadas e desabilitadas.
- Descoberta de dispositivos.
- Descoberta de clientes.
- Descoberta de redes.
- Descoberta de portas com protótipos para estado, velocidade negociada,
  velocidade máxima e tipo de conector.
- Velocidades vazias de porta são normalizadas para `0` Mbps, evitando erros de
  item numérico em portas desconectadas ou inativas.
- Descoberta de telemetria da Network API de portas em `port_table`, com estado do link,
  velocidade negociada, upload/download, erros RX/TX, descartes RX/TX, potência
  PoE, tensão PoE, estado PoE good, modo PoE e protótipos de gráfico.
- Valores booleanos da Network API são normalizados explicitamente, então strings da
  API como `false`, `0` e `down` são tratadas como inativas.
- Telemetria da Network API de portas usando um único item mestre com itens dependentes,
  evitando uma chamada à API por métrica em ambientes grandes.
- Descoberta de rádios com protótipos para canal, largura de canal, frequência e padrão WLAN.
- Saúde do sistema via `/proxy/network/api/s/default/stat/device`: CPU, memória,
  load average, storage agregado, uptime e temperatura de CPU.
- Descoberta de storage pelo endpoint da Network API com uso, livre, total, utilização,
  protótipos de trigger e protótipos de gráfico por volume.
- Saúde WAN pelo endpoint da Network API: latência, perda de pacote, disponibilidade,
  estado alive, IP WAN, upload/download e status, latência, última execução,
  idade, download e upload do speedtest.
- Visibilidade de failover WAN: WAN ativa, quantidade de WANs, estado de
  failover habilitado, estado de WAN primária ativa e estado de failover. Os
  itens WAN fixos de nível controller acompanham o uplink ativo quando o
  failover multi-WAN entra em ação.
- Descoberta WAN para ambientes multi-WAN. O ambiente testado possui uma WAN,
  mas o template inclui protótipos para WAN2 e outros rótulos WAN quando o
  payload da Network API os expõe, incluindo estado ativo, função e estado de
  failover por WAN.
- Telemetria de serviços de rede pelo endpoint da Network API: redes com DHCP,
  leases DHCP ativos, totais de túneis VPN/habilitados/up, modo IDS/IPS, regras
  de assinatura, versão da assinatura e idade da assinatura.
- Performance de rádio pelo endpoint da Network API: utilização de canal, self RX/TX,
  percentual de retries, estações conectadas e satisfaction.
- Performance da Network API de rádio usando um único item mestre com itens dependentes,
  evitando uma chamada à API por rádio/métrica em ambientes com muitos APs.
- Valores de radio satisfaction abaixo de zero são normalizados para `0`, pois
  alguns controllers UniFi retornam `-1` até a métrica estar disponível.
- Itens de saúde do coletor para Integration API, sistema via Network API, WAN
  via Network API, serviços de rede, portas e rádios. Eles indicam se o script retornou JSON utilizável
  e expõem o último erro da API/script em texto.
- Filtros de descoberta de baixo nível controlados por macros de host. O padrão
  é `.*`, então nada é excluído até que você altere as macros.
- Um dashboard chamado `UniFi Controller Overview` com gráficos clássicos de
  atividade de Internet, saúde do sistema e clientes/dispositivos.
- Um dashboard chamado `Unifi Controller` com gráfico SVG moderno, widget de
  versão e gauges de CPU/memória.
- Triggers para dispositivos offline, atualizações de firmware, redes
  desabilitadas, mudança de versão da aplicação, falhas do coletor, CPU alta,
  memória alta, storage alto, temperatura alta de CPU, latência WAN, perda WAN,
  baixa disponibilidade WAN, speedtest desatualizado, WAN primária inativa em
  failover, túneis VPN down, assinaturas IDS/IPS desatualizadas, alta utilização
  de rádio, retries altos e baixa satisfaction de rádio.

### Macros Úteis de Ajuste

Os limiares operacionais mais comuns ficam expostos como macros de host:

```text
{$UNIFI.CPU.WARN}
{$UNIFI.MEMORY.WARN}
{$UNIFI.STORAGE.WARN}
{$UNIFI.TEMP.WARN}
{$UNIFI.WAN.LATENCY.WARN}
{$UNIFI.WAN.LOSS.WARN}
{$UNIFI.WAN.AVAILABILITY.MIN}
{$UNIFI.SPEEDTEST.MAX_AGE}
{$UNIFI.IDS.SIGNATURE.MAX_AGE}
{$UNIFI.RADIO.UTIL.WARN}
{$UNIFI.RADIO.RETRY.WARN}
{$UNIFI.RADIO.SATISFACTION.MIN}
```

A descoberta de baixo nível pode ser reduzida com macros regex de inclusão. Os
padrões são permissivos:

```text
{$UNIFI.LLD.DEVICE.NAME.MATCHES} = .*
{$UNIFI.LLD.DEVICE.MODEL.MATCHES} = .*
{$UNIFI.LLD.NETWORK.NAME.MATCHES} = .*
{$UNIFI.LLD.CLIENT.TYPE.MATCHES} = .*
{$UNIFI.LLD.PORT.IDX.MATCHES} = .*
{$UNIFI.LLD.PORT.NAME.MATCHES} = .*
{$UNIFI.LLD.RADIO.INDEX.MATCHES} = .*
{$UNIFI.LLD.RADIO.BAND.MATCHES} = .*
{$UNIFI.LLD.STORAGE.MOUNT.MATCHES} = .*
{$UNIFI.LLD.WAN.NAME.MATCHES} = .*
```

Exemplo: para monitorar apenas APs cujo nome começa com `ap-`, defina
`{$UNIFI.LLD.DEVICE.NAME.MATCHES}` como `^ap-`.

### Solução de Problemas de Sem Dados

Quando um gráfico parar de receber dados, verifique primeiro estes itens no host
do controller:

```text
UniFi Integration API collection available
UniFi Integration API last error
UniFi Network API system collection available
UniFi Network API system last error
UniFi Network API WAN collection available
UniFi Network API WAN last error
UniFi port collection available
UniFi port last error
UniFi radio collection available
UniFi radio last error
```

Se um item de disponibilidade estiver `0`, o item `last error` correspondente
normalmente aponta para TLS, chave de API, firewall, site ID, Network API site ou
mudanças de endpoint.

## Script Externo

O script externo é:

```text
unifi_udm_pro_api.py
```

Ele usa apenas módulos da biblioteca padrão do Python, então não precisa de
dependências extras via `pip`.

Instale no diretório de scripts externos do servidor ou proxy Zabbix:

```bash
sudo install -m 0755 unifi_udm_pro_api.py /usr/lib/zabbix/externalscripts/unifi_udm_pro_api.py
```

### Ambiente de Teste Linux

Configure estas variáveis antes de testar:

```bash
export UNIFI_API_URL="https://xxx.xxx.xxx.xxx"
export UNIFI_SITE_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export UNIFI_API_KEY="replace-with-your-api-key"
```

Não armazene a chave real da API em arquivos versionados no Git.

`UNIFI_SITE_ID` é recomendado, mas opcional quando o controller possui apenas
um site. Nesse caso, o script descobre o site automaticamente.

### Comandos Brutos da API

```bash
./unifi_udm_pro_api.py info
./unifi_udm_pro_api.py sites
./unifi_udm_pro_api.py devices
./unifi_udm_pro_api.py clients
./unifi_udm_pro_api.py networks
./unifi_udm_pro_api.py device xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

A partir do diretório de scripts externos do Zabbix:

```bash
/usr/lib/zabbix/externalscripts/unifi_udm_pro_api.py info
/usr/lib/zabbix/externalscripts/unifi_udm_pro_api.py summary-devices
```

O script também aceita argumentos posicionais explícitos, útil para external
checks do Zabbix:

```bash
./unifi_udm_pro_api.py info "{$UNIFI.API.URL}" "{$UNIFI.API.KEY}"
./unifi_udm_pro_api.py devices "{$UNIFI.API.URL}" "{$UNIFI.API.KEY}" "{$UNIFI.SITE.ID}"
```

### Comandos de Resumo

```bash
./unifi_udm_pro_api.py summary-devices
./unifi_udm_pro_api.py summary-clients
./unifi_udm_pro_api.py summary-networks
./unifi_udm_pro_api.py system-health "$UNIFI_API_URL" "$UNIFI_API_KEY" default
./unifi_udm_pro_api.py wan-health "$UNIFI_API_URL" "$UNIFI_API_KEY" default
./unifi_udm_pro_api.py network-services "$UNIFI_API_URL" "$UNIFI_API_KEY" default
./unifi_udm_pro_api.py discover-wans "$UNIFI_API_URL" "$UNIFI_API_KEY" default
./unifi_udm_pro_api.py wan-field "$UNIFI_API_URL" "$UNIFI_API_KEY" default WAN latency_ms
```

`system-health` usa o endpoint da Network API do UniFi Network e retorna CPU, memória,
load, storage agregado, uptime e temperatura do UDM Pro. `wan-health` usa o
mesmo endpoint e retorna latência WAN, perda de pacotes, disponibilidade,
taxas de upload/download e dados de speedtest. `network-services` usa o mesmo
payload e retorna contadores resumidos de DHCP, VPN e IDS/IPS. `discover-wans` retorna linhas
de descoberta de baixo nível para interfaces WAN, preparado para `WAN`, `WAN2`
e outros objetos WAN expostos pelo UniFi.

### Comandos de Descoberta de Baixo Nível

```bash
./unifi_udm_pro_api.py discover-devices
./unifi_udm_pro_api.py discover-clients
./unifi_udm_pro_api.py discover-networks
./unifi_udm_pro_api.py discover-ports
./unifi_udm_pro_api.py discover-radios
./unifi_udm_pro_api.py discover-radio-performance "$UNIFI_API_URL" "$UNIFI_API_KEY" default
```

O script trata automaticamente endpoints paginados como `clients`. Quando
`discover-ports` ou `discover-radios` é chamado sem ID de dispositivo, ele
descobre os dispositivos primeiro e consulta detalhes apenas para dispositivos
que expõem `ports` ou `radios`.

Você ainda pode testar um único dispositivo manualmente:

```bash
./unifi_udm_pro_api.py discover-ports xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
./unifi_udm_pro_api.py discover-radios xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Próximas Adições Sugeridas

- Orçamento PoE por switch a partir de `total_used_power` e `total_max_power`.

### Notas de Revisão da API

O payload da Network API `stat/device` contém vários campos de alto valor para futuras
expansões do template:

- Identidade e firmware do gateway: `model`, `version`, `displayable_version`,
  `kernel_version`, `architecture` e `upgradable`.
- Saúde WAN: `last_wan_status`, `last_wan_interfaces`, `wan1`, `wan2`,
  `uplink`, `uptime_stats` e `speedtest-status`.
- Tráfego e portas: `port_table`, `uplink`, `downlink_table` e contadores por
  porta em `stat.sw`.
- PoE e energia: `poe_power`, `poe_voltage`, `poe_good`, `total_used_power`,
  `total_max_power` e flags de limite.
- Qualidade wireless: `radio_table_stats`, `vap_table`, percentual de retries,
  utilização de canal, quantidade de estações e satisfaction.
- Storage e temperatura: `storage`, `temperatures` e `overheating`.
- Segurança e IDS/IPS: quantidade de regras em `ids_ips_signature`, hora de
  atualização, tipo de assinatura e estado de ativação.
- Serviços de rede: `network_table`, status VPN, contagens de leases DHCP,
  leases IPv4 ativos, redes reportadas e estado de failover WAN.

## Respostas Locais da API Confirmadas

Os testes iniciais contra a API local do UDM Pro confirmaram a seguinte resposta
de site:

```json
{
  "offset": 0,
  "limit": 25,
  "count": 1,
  "totalCount": 1,
  "data": [
    {
      "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "internalReference": "default",
      "name": "Default"
    }
  ]
}
```

Valores confirmados do site:

- Site ID: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Referência interna: `default`
- Nome do site: `Default`

O endpoint info confirmou a versão da aplicação UniFi Network:

```json
{
  "applicationVersion": "10.3.58"
}
```

O endpoint de lista de dispositivos confirmou campos disponíveis para descoberta
de baixo nível:

- `id`
- `macAddress`
- `ipAddress`
- `name`
- `model`
- `state`
- `supported`
- `firmwareVersion`
- `firmwareUpdatable`
- `features`
- `interfaces`

O endpoint de lista de clientes confirmou descoberta paginada. A primeira
página retornou 25 clientes de um total de 28:

```json
{
  "offset": 0,
  "limit": 25,
  "count": 25,
  "totalCount": 28,
  "data": []
}
```

O coletor deve continuar requisitando páginas enquanto `offset + count` for
menor que `totalCount`.

Campos confirmados para descoberta de clientes:

- `type`
- `id`
- `name`
- `connectedAt`
- `ipAddress`
- `macAddress`
- `uplinkDeviceId`
- `access.type`

O endpoint de redes confirmou campos de VLAN e zona:

- `management`
- `id`
- `name`
- `enabled`
- `vlanId`
- `metadata.origin`
- `metadata.configurable`
- `zoneId`
- `default`

O site testado retornou 6 redes gerenciadas pelo gateway.

O endpoint de detalhe do UDM Pro confirmou dados por porta:

- `interfaces.ports[].idx`
- `interfaces.ports[].state`
- `interfaces.ports[].connector`
- `interfaces.ports[].maxSpeedMbps`
- `interfaces.ports[].speedMbps`

O endpoint de detalhe de um AP FlexHD confirmou uplink e dados de rádio:

- `adoptedAt`
- `provisionedAt`
- `configurationId`
- `uplink.deviceId`
- `interfaces.radios[].wlanStandard`
- `interfaces.radios[].frequencyGHz`
- `interfaces.radios[].channelWidthMHz`
- `interfaces.radios[].channel`

Objeto de porta de exemplo:

```json
{
  "idx": 1,
  "state": "UP",
  "connector": "RJ45",
  "maxSpeedMbps": 1000,
  "speedMbps": 1000
}
```

Objeto de rádio de exemplo:

```json
{
  "wlanStandard": "802.11ac",
  "frequencyGHz": 5,
  "channelWidthMHz": 40,
  "channel": 136
}
```

Candidatos de monitoramento confirmados pela API local oficial:

- Contagem de dispositivos.
- Estado do dispositivo.
- Suporte do dispositivo pela API.
- Versão de firmware do dispositivo.
- Disponibilidade de atualização de firmware.
- Endereço IP do dispositivo.
- Timestamp de provisionamento do dispositivo.
- ID de configuração do dispositivo.
- Descoberta de portas físicas.
- Estado de porta física.
- Tipo de conector físico.
- Velocidade máxima da porta física.
- Velocidade negociada da porta física.
- Versão da aplicação UniFi Network.
- Dispositivo de uplink do AP.
- Descoberta de rádio do AP.
- Padrão WLAN do rádio.
- Banda/frequência do rádio.
- Largura de canal do rádio.
- Canal do rádio.
- Contagem de clientes.
- Contagem de clientes sem fio.
- Contagem de clientes cabeados.
- Descoberta de clientes.
- IP do cliente.
- Dispositivo de uplink do cliente.
- Tipo de acesso do cliente.
- Contagem de redes.
- Estado habilitado da rede.
- VLAN ID da rede.
- Tipo de gerenciamento da rede.
- Origem de metadata da rede.
- Zone ID da rede.
- Flag de rede padrão.

Testes Linux confirmados a partir do diretório de scripts externos do Zabbix:

```bash
./unifi_udm_pro_api.py summary-devices
```

Retornou:

```json
{"offline":0,"online":5,"total":5,"updatable":0}
```

```bash
./unifi_udm_pro_api.py discover-devices
```

Retornou 5 dispositivos UniFi descobertos.

```bash
./unifi_udm_pro_api.py discover-ports xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Retornou 11 portas do UDM Pro descobertas.

Candidatos de trigger confirmados:

- Dispositivo não está `ONLINE`.
- Dispositivo não é suportado pela API.
- Atualização de firmware disponível.
- Endereço IP do dispositivo mudou.
- Versão de firmware mudou.
- Porta física esperada como ativa está down.
- Porta física negociada abaixo da velocidade máxima.
- Velocidade da porta física mudou.
- Uplink do AP mudou.
- Canal do rádio do AP mudou.
- Largura de canal do rádio do AP mudou.
- Cliente importante desconectou ou desapareceu da descoberta.
- IP do cliente mudou.
- Uplink do cliente mudou.
- Tipo de acesso inesperado do cliente.
- Rede desabilitada inesperadamente.
- VLAN ID da rede mudou.
- Zona da rede mudou.
- Rede padrão mudou.
