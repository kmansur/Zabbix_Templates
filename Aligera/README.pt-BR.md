# Templates Zabbix para Aligera

[English](README.md) | **Português (Brasil)**

Instalação: [English](INSTALL.md) | **[Português (Brasil)](INSTALL.pt-BR.md)**

Este diretório contém templates Zabbix para monitoramento de gateways de telecomunicações Aligera.

## Aligera AG561 E1 by SNMP

O template do AG561 foi adaptado e expandido para o Zabbix 7.0 utilizando a MIB enterprise da Aligera (`1.3.6.1.4.1.41933`), SNMPv2-MIB e IF-MIB, e foi validado em equipamentos Aligera AG561 reais.

Arquivo do template: [`7.0/template_aligera_ag561_e1_snmp.yaml`](7.0/template_aligera_ag561_e1_snmp.yaml)

### Ambiente validado

- Equipamento: Aligera AG561
- Firmware testado: 8.16
- Zabbix: 7.0
- SNMP: v2c
- Versão do template: 3.0.0
- Vendor do template: Net Tech
- Grupo do template: `Templates/Network devices`

## Cobertura de monitoramento

### Equipamento e SNMP

- Nome do produto
- Descrição do sistema e firmware
- Uptime do equipamento
- Disponibilidade SNMP
- Disponibilidade ICMP
- Perda de pacotes ICMP
- Latência ICMP
- Nome SNMP do sistema, contato, localização e Object ID

### E1

- Quantidade de interfaces E1
- Estado atual de alarme da E1
- Tempo das estatísticas E1
- Code violations
- Slips
- Erros CRC
- Eventos LOS e tempo acumulado em LOS
- Eventos AIS e tempo acumulado em AIS
- Eventos BFAE e tempo acumulado em BFAE
- Eventos MFAE e tempo acumulado em MFAE
- Eventos RAI e tempo acumulado em RAI
- Taxas de erros/eventos
- Métricas de qualidade recente
- Eventos normalizados por hora
- Percentuais de duração de alarmes
- Percentual operacional de tempo saudável
- Detecção de reset das estatísticas E1

### Canais de voz

A descoberta de canais utiliza a tabela da Aligera e exclui entradas `SIG(6)` do monitoramento de voz.

Na configuração validada:

- Entradas na tabela de canais: 31
- Canais de voz: 30
- Entrada de sinalização: TS16 / `SIG(6)`

O template monitora tipo/estado do canal, canais livres/ocupados/bloqueados/N/A, utilização e picos de ocupação/utilização em 24 horas.

### SIP

A descoberta de peers SIP inclui nome, host/IP, porta, Keepalive e Registry. Como Keepalive e Registry são strings na MIB, o template registra mudanças informativas sem assumir que `Unmonitored` ou `-` representem falha.

### Ethernet / IF-MIB

As interfaces Ethernet são descobertas por `ifType=6` (`ethernetCsmacd`). O template monitora estado administrativo/operacional, MTU, MAC, tráfego RX/TX de 64 bits, erros, discards e suas taxas de crescimento. Interfaces administrativamente desabilitadas não geram problema de link down.

## Macros de usuário

Abaixo estão todas as **15 macros** exportadas pela versão 3.0.0 do template. Elas podem ser sobrescritas no nível do host quando um AG561 tiver capacidade ou baseline operacional diferente.

| Macro | Padrão | Finalidade |
|---|---:|---|
| `{$AG561.CHANNEL.NA.WARN}` | `1` | Quantidade mínima de canais de voz em N/A que gera Warning quando persistir por 5 minutos. |
| `{$AG561.CHANNEL.UTIL.HIGH}` | `90` | Percentual médio de utilização dos canais em 5 minutos para alerta High. |
| `{$AG561.CHANNEL.UTIL.WARN}` | `80` | Percentual médio de utilização dos canais em 5 minutos para alerta Warning. |
| `{$AG561.E1.EXPECTED}` | `1` | Quantidade esperada de interfaces E1. Pode ser sobrescrita no host. |
| `{$AG561.SIG.EXPECTED}` | `1` | Quantidade esperada de entradas SIG. Pode ser sobrescrita no host. |
| `{$AG561.SIP.EXPECTED}` | `1` | Quantidade esperada de peers SIP. Pode ser sobrescrita no host. |
| `{$AG561.VOICE.EXPECTED}` | `30` | Quantidade esperada de canais de voz. Pode ser sobrescrita no host. |
| `{$E1.CODE.RATE.WARN}` | `0` | Taxa de Code Violations/s acima deste valor gera alerta. Zero significa alertar em qualquer aumento. |
| `{$E1.CRC.RATE.WARN}` | `0` | Taxa de erros CRC/s acima deste valor gera alerta. Zero significa alertar em qualquer aumento. |
| `{$E1.SLIP.RATE.HIGH}` | `0.1` | Taxa persistente de Slips/s para alerta High após 15 minutos. Ajustar após observar o baseline real. |
| `{$E1.SLIP.RATE.WARN}` | `0` | Taxa de Slips/s acima deste valor gera alerta. Zero significa alertar em qualquer aumento. |
| `{$ICMP.LOSS.WARN}` | `20` | Perda média de pacotes ICMP (%) que gera alerta Warning. |
| `{$ICMP.RESPONSE.WARN}` | `100` | Latência média ICMP em milissegundos que gera alerta Warning. |
| `{$IF.DISCARD.RATE.WARN}` | `0` | Taxa de discards RX/TX por segundo acima deste valor gera Warning. Zero alerta em qualquer aumento persistente. |
| `{$IF.ERROR.RATE.WARN}` | `0` | Taxa de erros RX/TX por segundo acima deste valor gera Warning. Zero alerta em qualquer aumento persistente. |

### Observações para ajuste das macros

- As quatro macros `*.EXPECTED` devem refletir a configuração real. O AG561 validado usa 1 E1, 30 canais de voz, 1 entrada SIG e 1 peer SIP.
- As macros de taxa com padrão `0` alertam intencionalmente em qualquer novo crescimento. Eleve os limites somente depois de observar um baseline saudável.
- `{$E1.SLIP.RATE.HIGH}` é independente do limite Warning e deve ser calibrada com histórico de produção.
- Limites de ICMP e utilização de canais são valores operacionais iniciais e podem ser sobrescritos por host.

## Triggers

O template inclui triggers para disponibilidade ICMP/SNMP, perda e latência, canais BLOCKED/N/A, utilização dos canais, E1 LOS/AIS/BFAE/MFAE/RAI, crescimento de CRC/slips/code violations, slips persistentes, reset das estatísticas E1, reboot, link Ethernet, erros/discards, divergência de capacidade e mudanças informativas de SIP/firmware.

## Dashboards

O template inclui:

- Operational view
- Diagnostics
- Capacity
- SIP

O Honeycomb operacional exibe apenas os 30 canais de voz e exclui o timeslot de sinalização.

## SNMP Traps

A versão 3.x suporta:

- `e1AlarmsChange` — `1.3.6.1.4.1.41933.1.2.3.1`
- `chanStatusChange` — `1.3.6.1.4.1.41933.1.3.3.1`
- `sipKeepaliveChange` — `1.3.6.1.4.1.41933.1.4.3.1`
- `snmptrap.fallback` para traps não reconhecidas

Os eventos de trap são informativos e complementares; as triggers de polling continuam sendo a referência para o estado persistente da falha.

Para instalação completa e configuração do receptor de traps, consulte **[INSTALL.pt-BR.md](INSTALL.pt-BR.md)**.

## Observações importantes

- Os contadores brutos da E1 são cumulativos desde o último reset das estatísticas E1. Um valor histórico diferente de zero não representa, por si só, uma falha ativa.
- Itens baseados em taxa e qualidade recente detectam degradação ativa.
- Percentuais de duração de alarmes e tempo saudável são indicadores operacionais, não medições contratuais de SLA.
- O equipamento pode retornar `chanNumber=31`; nos equipamentos validados existem 30 canais de voz MFCR2 e uma entrada `SIG` no TS16.
- `ifSpeed` / `ifHighSpeed` não são utilizados porque o firmware AG561 testado retornou valores não confiáveis nas interfaces Ethernet físicas.
- SNMPv2c não possui criptografia. Utilize apenas em rede privada/confiável e restrinja UDP/161 e UDP/162 por firewall.

## Créditos

O trabalho inicial foi baseado no template Zabbix para AG562 desenvolvido por Douglas Boldrini:

- Repositório original: https://github.com/boldrinidouglas/ZBX-GRA-ALIGERA
- Template original: `TEMPLATE_TELEFONIA_AG562_E1_LLD_SNMP_ZBX-5.0.xml`

A adaptação para AG561, modernização para Zabbix 7.0, ampliação da cobertura da MIB, dashboards, triggers, métricas de capacidade, monitoramento IF-MIB e suporte a SNMP traps foram desenvolvidos e validados para o ambiente Net Tech.
