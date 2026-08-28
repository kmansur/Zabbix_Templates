# Templates Zabbix para Aligera

[English](README.md) | **Português (Brasil)**

Este diretório contém templates Zabbix para monitoramento de gateways de telecomunicações Aligera.

## Aligera AG561 E1 by SNMP

O template do AG561 foi adaptado e expandido para o Zabbix 7.0 utilizando a MIB enterprise da Aligera (`1.3.6.1.4.1.41933`), SNMPv2-MIB e IF-MIB, e foi validado em equipamentos Aligera AG561 reais.

### Ambiente validado

- Equipamento: Aligera AG561
- Firmware testado: 8.16
- Zabbix: 7.0
- SNMP: v2c
- Vendor do template: Net Tech
- Grupo do template: `Templates/Network devices`

## Cobertura de monitoramento

O template inclui monitoramento das seguintes áreas.

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

A descoberta de canais utiliza a tabela de canais da Aligera e exclui entradas `SIG(6)` do monitoramento de voz.

Na configuração do AG561 validada:

- Entradas na tabela de canais: 31
- Canais de voz: 30
- Entrada de sinalização: TS16 / `SIG(6)`

O template monitora:

- Tipo do canal
- Estado do canal: BLOCKED, IDLE, BUSY, N/A
- Canais livres
- Canais ocupados
- Canais bloqueados
- Canais em N/A
- Percentual de utilização dos canais
- Pico de canais ocupados nas últimas 24 horas
- Pico de utilização nas últimas 24 horas

### SIP

A descoberta de peers SIP inclui:

- Nome do peer
- Host/IP
- Porta
- Estado de Keepalive
- Estado de Registry

A MIB da Aligera expõe Keepalive e Registry como strings, e não como estados enumerados. Por esse motivo, o template registra eventos informativos quando esses valores mudam, mas não assume que valores como `Unmonitored` ou `-` representem falha.

### Ethernet / IF-MIB

As interfaces Ethernet são descobertas utilizando `ifType=6` (`ethernetCsmacd`).

O template monitora:

- Estado administrativo
- Estado operacional
- MTU
- Endereço MAC
- Tráfego RX de 64 bits via `ifHCInOctets`
- Tráfego TX de 64 bits via `ifHCOutOctets`
- Erros RX
- Erros TX
- Discards RX
- Discards TX
- Taxas de crescimento de erros e discards

Interfaces administrativamente desabilitadas não geram problemas de link down.

## Triggers

O template inclui triggers para, entre outras condições:

- Indisponibilidade ICMP
- Indisponibilidade SNMP
- Perda de pacotes
- Latência ICMP elevada
- Canal de voz BLOCKED
- Canal de voz N/A
- Utilização elevada dos canais
- E1 LOS
- E1 AIS
- E1 BFAE
- E1 MFAE
- E1 RAI
- Crescimento de erros CRC
- Crescimento de slips
- Slips persistentes
- Crescimento de code violations
- Reset das estatísticas E1
- Reboot do equipamento
- Interface Ethernet operacionalmente down enquanto administrativamente up
- Crescimento de erros/discards Ethernet
- Divergência de configuração/capacidade
- Mudanças informativas de configuração/estado SIP
- Mudanças informativas de firmware/descrição do sistema

Os limites configuráveis são expostos por macros de usuário do Zabbix sempre que apropriado.

## Dashboards

O template inclui dashboards de template para:

- Operational view
- Diagnostics
- Capacity
- SIP

O Honeycomb operacional dos canais exibe somente os 30 canais de voz e exclui o timeslot de sinalização.

## SNMP Traps

A versão 3.x adiciona suporte às notificações Aligera definidas na MIB:

- `e1AlarmsChange`
- `chanStatusChange`
- `sipKeepaliveChange`

O template também inclui um item fallback para SNMP traps não reconhecidos, útil para diagnóstico e futuras expansões.

### Requisitos do receptor de traps no Zabbix

A importação do template não configura automaticamente o receptor de SNMP traps do sistema operacional. O Zabbix Server ou Proxy responsável por receber as traps precisa ter o processamento habilitado, por exemplo:

```ini
StartSNMPTrapper=1
SNMPTrapperFile=/var/log/snmptrap/snmptrap.log
```

O `snmptrapd`, ou outro handler compatível, deve gravar as traps recebidas no formato esperado pelo Zabbix. O AG561 também precisa ser configurado para enviar as traps para o endereço IP do Zabbix Server ou Proxy responsável pelo host monitorado.

## Observações importantes

- Os contadores brutos da E1 são cumulativos desde o último reset das estatísticas E1. Um valor histórico diferente de zero não representa, por si só, uma falha ativa.
- Itens baseados em taxa e métricas de qualidade recente são utilizados para detectar degradação ativa.
- Os percentuais de duração de alarmes e de tempo saudável da E1 são indicadores operacionais, não medições contratuais de SLA.
- O equipamento pode retornar `chanNumber=31`; nos equipamentos validados existem 30 canais de voz MFCR2 e uma entrada de sinalização (`SIG`) no TS16.
- `ifSpeed` / `ifHighSpeed` não são utilizados porque o firmware AG561 testado retornou valores não confiáveis para as interfaces Ethernet físicas.

## Créditos

O trabalho inicial foi baseado no template Zabbix para AG562 desenvolvido por Douglas Boldrini:

- Repositório original: https://github.com/boldrinidouglas/ZBX-GRA-ALIGERA
- Template original: `TEMPLATE_TELEFONIA_AG562_E1_LLD_SNMP_ZBX-5.0.xml`

A adaptação para AG561, modernização para Zabbix 7.0, ampliação da cobertura da MIB, dashboards, triggers, métricas de capacidade, monitoramento IF-MIB e suporte a SNMP traps foram desenvolvidos e validados para o ambiente Net Tech.
