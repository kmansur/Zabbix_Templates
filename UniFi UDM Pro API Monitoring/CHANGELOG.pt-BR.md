# Histórico de alterações

## 0.8.0 - 2026-09-04

- Unificação do monitoramento UniFi em **um template por versão principal do Zabbix** e **um único coletor externo**: `unifi_udm_pro_api.py`.
- Remoção do modelo temporário com template complementar do dashboard e `unifi_dashboard_telemetry.py`.
- Inclusão de janelas móveis de tráfego por cliente e aplicação DPI em `1h`, `1d`, `1w` e `1m` (30 dias).
- Inclusão de RSSI atual dos clientes Wi-Fi e métricas de associação/autenticação/DHCP/DNS.
- Resolução dos nomes das aplicações DPI pelo catálogo da Integration API usando o ID composto `(category << 16) + application`.
- Otimização da coleta do dashboard: uma única consulta v2 `/traffic` fornece ranking de clientes e aplicações para cada janela.
- Validação do endpoint v2 de tráfego com timestamps Unix epoch em milissegundos no UniFi Network 10.6.101.
- Testes reais das janelas de 1 semana e 30 dias com aproximadamente 0,74 s e 1,00 s de resposta.
- Remoção das chaves temporárias de ranking com um único argumento; o Dashboard 0.2 usa somente os contratos com período.
- Simplificação da estrutura do repositório e da documentação de instalação.

## 0.7.0 - 2026-09-04

- Suporte ao UniFi Network 10.6 usando o endpoint documentado `statistics/latest` da Integration API em conjunto com a telemetria operacional existente.
- Inclusão de CPU, memória, load average, uptime e RX/TX do uplink.
- Inclusão de itens de saúde/erro do coletor da API oficial.
- Verificação TLS opcional por meio de `{$UNIFI.TLS.ARG}`.
- Atualização da documentação da chave de API para **UniFi Network > Integrations**.

O histórico anterior continua disponível no Git e nos pull requests já mesclados.
