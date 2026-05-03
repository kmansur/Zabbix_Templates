# Changelog

Versão em inglês: [CHANGELOG.md](CHANGELOG.md)

Todas as mudanças relevantes deste projeto são documentadas aqui.

Manutenção da documentação: quando o `CHANGELOG.md` em inglês for atualizado,
atualize este `CHANGELOG.pt-BR.md` na mesma alteração.

## 0.6.5 - Não Lançado

### Adicionado

- Adicionada coleta de orçamento PoE por dispositivo a partir dos campos de
  energia da Network API e dos dados de portas com capacidade PoE.
- Adicionada descoberta de baixo nível de orçamento PoE com protótipos para
  usado, máximo, disponível, utilização, quantidade de portas PoE e estado
  near-limit.
- Adicionados protótipos de trigger de aviso para alta utilização de orçamento
  PoE e flags explícitas de PoE near-limit.
- Adicionados protótipos de gráfico de orçamento PoE e itens de saúde do
  coletor.
- Adicionada a macro `{$UNIFI.POE.BUDGET.WARN}` para ajuste da utilização do
  orçamento PoE.

### Alterado

- Atualizada a versão do script para `0.6.5`.
- Atualizada a versão do vendor do template para `0.6-5`.

## 0.6.4 - Não Lançado

### Adicionado

- Adicionada coleta `network-services` a partir do payload de dispositivo da
  Network API para telemetria de DHCP, VPN e IDS/IPS.
- Adicionados contadores de redes com DHCP habilitado e leases ativos.
- Adicionados contadores de túneis VPN totais, habilitados e up, com trigger de
  aviso quando túneis VPN habilitados não estão up.
- Adicionados estado habilitado, modo, quantidade de regras, versão da
  assinatura, última atualização e idade de assinatura IDS/IPS, com trigger de
  aviso para assinatura desatualizada.
- Adicionados itens de saúde do coletor para o item mestre de serviços de rede.
- Adicionada a macro `{$UNIFI.IDS.SIGNATURE.MAX_AGE}` para ajuste da idade da
  assinatura IDS/IPS.

### Alterado

- Atualizada a versão do script para `0.6.4`.
- Atualizada a versão do vendor do template para `0.6-4`.

## 0.6.3 - Não Lançado

### Adicionado

- Adicionada visibilidade de failover WAN para ambientes multi-WAN: WAN ativa,
  quantidade de WANs, estado de failover habilitado, estado de WAN primária
  ativa e estado de failover.
- Adicionados metadados por WAN na descoberta: função, estado ativo e estado
  de failover.
- Adicionada trigger de aviso quando multi-WAN/failover está disponível, mas a
  WAN primária não é mais o uplink ativo.
- Itens WAN fixos de nível controller agora acompanham o uplink ativo quando
  nenhum rótulo WAN é passado, enquanto os protótipos por WAN mantêm rótulos
  explícitos.

### Alterado

- Atualizada a versão do script para `0.6.3`.
- Atualizada a versão do vendor do template para `0.6-3`.

## 0.6.2 - Não Lançado

### Alterado

- Removido `legacy` dos nomes visíveis de itens, triggers, gráficos e keys do
  template. O template agora usa a nomenclatura Network API para essas métricas.
- Renomeada a macro de site da Network API de `{$UNIFI.LEGACY.SITE}` para
  `{$UNIFI.NETWORK.SITE}`.
- Adicionados aliases de comandos no script, como `port-telemetry`,
  `discover-port-telemetry`, `radio-performance` e
  `discover-radio-performance`, mantendo os nomes anteriores para
  compatibilidade em testes manuais.
- Atualizada a versão do vendor do template para `0.6-2`.

## 0.6.1 - Não Lançado

### Corrigido

- Aumentada a legenda do widget `UniFi Clients` no dashboard de duas para três
  linhas, para que as três séries de clientes fiquem visíveis no dashboard
  `Unifi Controller`.

### Alterado

- Atualizada a versão do vendor do template para `0.6-1`.

## 0.6.0 - Não Lançado

### Adicionado

- Adicionados itens dependentes e triggers de saúde do coletor para Integration
  API, legacy system, legacy WAN, legacy port e legacy radio.
- Adicionados itens de texto de último erro para as mesmas superfícies do
  coletor, facilitando o troubleshooting de sem dados.
- Adicionadas macros de filtro de inclusão para descoberta de baixo nível de
  dispositivos, redes, clientes, portas, rádios, storage e labels WAN.
- Adicionadas triggers de aviso para baixa disponibilidade WAN, alta utilização
  de rádio, percentual alto de retries de rádio e baixa satisfaction de rádio.

### Alterado

- Atualizada a versão do script para `0.6.0`.
- Atualizada a versão do vendor do template para `0.6-0`.
- Substituído o dashboard `Unifi Controller` por um layout separado com tráfego
  WAN, qualidade WAN, clientes e gauges de sistema.

### Corrigido

- Corrigida a montagem da URL da API legada quando `{$UNIFI.API.URL}` é
  configurada com o caminho completo `/proxy/network/integration/v1` em vez de
  apenas a raiz do UDM Pro.
- Corrigida a normalização booleana de campos legados de porta, PoE e estado
  WAN para que strings como `false`, `0` e `down` não sejam tratadas como
  ativas.

## 0.5.3 - Não Lançado Anterior

### Corrigido

- Removido `{$UNIFI.DEVICE.ID}` das chaves dos itens mestres fixos de sistema e
  WAN para que gráficos de nível controller continuem funcionando mesmo quando
  um host possui macro de device ID incompatível. O script ainda suporta IDs
  explícitos para testes manuais de endpoints legados.
- Tratadas macros de usuário Zabbix não resolvidas, como `{$UNIFI.DEVICE.ID}`,
  como argumentos opcionais vazios no script.
- Adicionado fallback para o legacy site `default` quando o argumento de legacy
  site opcional estiver vazio ou não resolvido.

### Alterado

- Atualizada a versão do script para `0.5.3`.
- Atualizada a versão do vendor do template para `0.5-3`.

## 0.5.2 - Não Lançado Anterior

### Adicionado

- Adicionado o comando mestre `legacy-radios`, que retorna telemetria legada de
  performance de rádios normalizada como um mapa compacto dispositivo/rádio.

### Alterado

- Convertidos os protótipos de itens de performance legada de rádio de external
  checks para itens dependentes apoiados pelo item mestre `legacy-radios`.
- Mantido `legacy-radio-field` disponível para testes manuais e compatibilidade.
- Atualizada a versão do script para `0.5.2`.
- Atualizada a versão do vendor do template para `0.5-2`.

## 0.5.1 - Não Lançado Anterior

### Adicionado

- Adicionado o comando mestre `legacy-ports`, que retorna telemetria legada de
  portas normalizada como um mapa compacto dispositivo/porta.

### Alterado

- Convertidos os protótipos de itens de telemetria legada de portas de external
  checks para itens dependentes apoiados pelo item mestre `legacy-ports`.
- Mantido `legacy-port-field` disponível para testes manuais e compatibilidade.
- Atualizada a versão do script para `0.5.1`.
- Atualizada a versão do vendor do template para `0.5-1`.

## 0.5.0 - Não Lançado Anterior

### Adicionado

- Adicionada descoberta de telemetria legada de portas a partir de `port_table`,
  com protótipos para estado do link, velocidade negociada, taxas de tráfego,
  erros RX/TX, descartes RX/TX, potência PoE, tensão PoE, estado PoE good e
  modo PoE.
- Adicionados protótipos de gráficos para tráfego, erros/descartes e PoE em
  portas legadas.
- Adicionados os comandos `legacy-discover-ports` e `legacy-port-field`.

### Alterado

- Atualizada a versão do script para `0.5.0`.
- Atualizada a versão do vendor do template para `0.5-0`.

## 0.4.4 - Não Lançado Anterior

### Corrigido

- Normalizados valores vazios de velocidade e velocidade máxima de porta para
  `0`, evitando que itens numéricos unsigned do Zabbix rejeitem placeholders de
  portas inativas.

### Alterado

- Atualizada a versão do script para `0.4.4`.
- Atualizada a versão do vendor do template para `0.4-4`.

## 0.4.3 - Não Lançado Anterior

### Corrigido

- Normalizados valores negativos de satisfaction de rádio legado para `0`, para
  que itens numéricos unsigned do Zabbix não rejeitem placeholders UniFi `-1`.

### Alterado

- Atualizada a versão do script para `0.4.3`.
- Atualizada a versão do vendor do template para `0.4-3`.

## 0.4.2 - Não Lançado Anterior

### Corrigido

- Removida a trigger de alteração de endereço IP WAN porque o import do Zabbix
  alvo rejeitou a função de trigger `diff()`.

### Alterado

- Atualizada a versão do script para `0.4.2`.
- Atualizada a versão do vendor do template para `0.4-2`.

## 0.4.1 - Não Lançado Anterior

### Corrigido

- Corrigida a estrutura de exportação da página do dashboard `Unifi Controller`
  adicionando uma página nomeada antes da lista `widgets`.

### Alterado

- Atualizada a versão do script para `0.4.1`.
- Atualizada a versão do vendor do template para `0.4-1`.

## 0.4.0 - Não Lançado Anterior

### Adicionado

- Adicionados itens WAN fixos para estado alive, endereço IP, latência do
  speedtest, última execução do speedtest, idade do speedtest e status do
  speedtest.
- Adicionado item fixo de uptime do sistema a partir do item mestre de saúde do
  sistema existente.
- Adicionada trigger informativa para resultados de speedtest WAN desatualizados.
- Adicionada trigger informativa para alteração do endereço IP WAN.
- Adicionado o dashboard `Unifi Controller` com gráfico SVG moderno, widget de
  versão e gauges de CPU/memória.
- Adicionadas notas de revisão da API ao README com campos candidatos para as
  próximas iterações do template.

### Alterado

- Removido o dashboard experimental anterior.
- Atualizada a versão do script para `0.4.0`.
- Atualizada a versão do vendor do template para `0.4-0`.

## 0.3.3 - Não Lançado Anterior

### Adicionado

- Adicionada descoberta de volumes de storage ao template.
- Adicionados protótipos de itens por storage para usado, livre, total e utilização.
- Adicionados protótipos de triggers e gráficos de uso por storage.

### Corrigido

- Permitido que `storage-field` selecione automaticamente o dispositivo UDM,
  alinhando o comportamento com `discover-storage` e os helpers de WAN.
- Movido o protótipo de trigger WAN alive para o nível da regra de descoberta,
  melhorando compatibilidade de importação no Zabbix.

### Alterado

- Atualizada a versão do script para `0.3.3`.
- Atualizada a versão do vendor do template para `0.3-3`.

## 0.3.2 - Não Lançado Anterior

### Corrigido

- Mascarados identificadores reais restantes nos exemplos do README e nas notas
  de respostas confirmadas da API.
- Substituída a URL padrão da API no template por um valor placeholder.
- Substituído o exemplo de URL no docstring do script por um placeholder genérico.

### Alterado

- Atualizada a versão do script para `0.3.2`.
- Atualizada a versão do vendor do template para `0.3-2`.

## 0.3.1 - Não Lançado Anterior

### Corrigido

- Corrigidos protótipos de itens de descoberta WAN retornando
  `{"error":"missing WAN field arguments"}` quando `{$UNIFI.DEVICE.ID}` está vazio.
- Simplificadas as chaves dos protótipos WAN para que `wan-field` use o
  dispositivo UDM detectado automaticamente por padrão: URL, chave de API,
  legacy site, nome WAN e campo.
- Mantida compatibilidade no script para chaves antigas de `wan-field` que ainda
  passam um ID explícito de dispositivo antes do nome da WAN.

### Alterado

- Atualizada a versão do script para `0.3.1`.
- Atualizada a versão do vendor do template para `0.3-1`.

## 0.3.0 - Não Lançado Anterior

### Adicionado

- Adicionado versionamento explícito do projeto no script externo e nos metadados
  de vendor do template Zabbix.
- Melhorada a documentação do script e docstrings para superfícies de API,
  tratamento de erros, helpers de descoberta, helpers de item escalar, saúde do
  sistema, saúde WAN e telemetria de rádio.
- Adicionada descoberta multi-WAN com o comando `discover-wans`.
- Adicionada coleta escalar `wan-field` para protótipos de itens WAN.
- Adicionada descoberta de baixo nível WAN ao template Zabbix:
  - Latência WAN.
  - Perda de pacotes WAN.
  - Disponibilidade WAN.
  - Download WAN.
  - Upload WAN.
  - Estado alive WAN.
  - Protótipo de gráfico de atividade de Internet por WAN.
- Adicionado `UniFi Controller Overview - Experimental`, um segundo dashboard
  focado em layout semelhante ao UniFi, com páginas Internet, Wireless e System.
- Adicionado gráfico `UniFi WAN quality` para latência, perda e disponibilidade.

### Alterado

- Mantidos os itens originais de WAN única para instalações simples de UDM Pro,
  enquanto a descoberta WAN foi adicionada para futuras instalações multi-WAN.
- Atualizada a versão do script para `0.3.0`.
- Atualizada a versão do vendor do template para `0.3-0`.

### Notas

- O suporte multi-WAN foi implementado a partir da estrutura do payload legado
  (`uptime_stats`, `last_wan_interfaces`, `wan1`, `wan2` e `uplink`), mas o
  ambiente atual de teste possui apenas uma WAN. Uma importação real multi-WAN
  deve ser validada quando houver um dispositivo com WAN2 disponível.

## 0.2.0 - Não Lançado Anterior

### Adicionado

- Adicionado suporte à API legada do UniFi Network em
  `/proxy/network/api/s/<site>/stat/device`.
- Adicionada coleta de saúde do sistema do UDM Pro:
  - Utilização de CPU.
  - Utilização de memória.
  - Load average.
  - Uso agregado de storage.
  - Temperatura de CPU.
- Adicionada coleta de saúde WAN:
  - Latência WAN.
  - Perda de pacotes derivada da disponibilidade WAN.
  - Taxas de upload e download WAN.
  - Download, upload e latência do speedtest.
- Adicionado dashboard `UniFi Controller Overview` com gráficos de atividade de
  Internet, saúde do sistema e clientes/dispositivos.
- Adicionadas definições de gráficos para atividade de Internet, saúde do sistema
  e clientes.
- Adicionada descoberta de performance legada de rádio a partir de
  `radio_table_stats`.
- Adicionados protótipos de itens de performance de rádio:
  - Utilização de canal (`cu_total`).
  - Utilização self RX.
  - Utilização self TX.
  - Percentual de retries TX.
  - Estações conectadas.
  - Satisfaction.
- Adicionados protótipos de gráficos para utilização de canal e qualidade de rádio.

### Alterado

- Expandido o template Zabbix com saúde do sistema, storage, saúde WAN e macros
  de dashboard.
- Estendido o script externo com `legacy-discover-radios` e `legacy-radio-field`.

## 0.1.0 - Desenvolvimento Inicial

### Adicionado

- Criado o diretório do projeto `UniFi UDM Pro API Monitoring`.
- Adicionado README do projeto com criação de chave de API e recomendações de segurança.
- Adicionado o script externo `unifi_udm_pro_api.py`.
- Adicionado suporte à API local UniFi Network Integration:
  - `info`
  - `sites`
  - `devices`
  - `clients`
  - `networks`
  - `device`
  - `client`
- Adicionado suporte automático a paginação.
- Adicionados comandos de descoberta de baixo nível para Zabbix:
  - Dispositivos.
  - Clientes.
  - Redes.
  - Portas.
  - Rádios.
- Adicionados comandos de resumo para dispositivos, clientes e redes.
- Adicionado um template importável para Zabbix 7.0.
- Adicionadas descobertas de dispositivos, clientes, redes, portas e rádios ao template.
- Adicionadas triggers para dispositivos offline, atualizações de firmware, redes
  desabilitadas e mudanças de versão da aplicação.

### Corrigido

- Removidas tags não suportadas de regras de descoberta para compatibilidade com
  importação no Zabbix 7.0.
- Substituídos UUIDs determinísticos UUIDv5 por UUIDv4 aceitos pelo Zabbix.
- Normalizados valores booleanos de macros de descoberta para `true` e `false`
  em minúsculas.
