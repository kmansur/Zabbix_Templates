# Instalação e Configuração — Aligera AG561 E1 by SNMP

[English](INSTALL.md) | **Português (Brasil)**

Voltar para: [README.pt-BR.md](README.pt-BR.md)

Este guia cobre a instalação e configuração do template `Aligera AG561 E1 by SNMP` para Zabbix 7.0, incluindo polling SNMP e recepção de SNMP traps.

Arquivo do template: [`7.0/template_aligera_ag561_e1_snmp.yaml`](7.0/template_aligera_ag561_e1_snmp.yaml)

## 1. Ambiente validado

- Equipamento: Aligera AG561
- Firmware testado: 8.16
- Zabbix: 7.0
- Polling SNMP: SNMPv2c
- Versão do template: 3.0.0
- Vendor do template: Net Tech
- Grupo: `Templates/Network devices`
- OID enterprise da Aligera: `1.3.6.1.4.1.41933`

O template também utiliza objetos da SNMPv2-MIB e IF-MIB.

## 2. Requisitos de rede

Libere somente o tráfego necessário entre o sistema de monitoramento e os AG561:

| Direção | Protocolo/porta | Finalidade |
|---|---|---|
| Zabbix Server/Proxy → AG561 | UDP/161 | Polling SNMP |
| AG561 → Zabbix Server/Proxy | UDP/162 | SNMP traps |
| Zabbix Server/Proxy → AG561 | ICMP | Disponibilidade, perda e latência |

Para SNMPv2c, utilize uma community dedicada e mantenha o tráfego em rede privada/confiável. SNMPv2c não possui criptografia nem autenticação forte do remetente.

## 3. Instalar ferramentas SNMP no Zabbix Server ou Proxy

Exemplo para Debian/Ubuntu:

```bash
apt update
apt install -y snmp snmptrapd curl
```

O pacote `snmp` fornece `snmpget`, `snmpwalk` e `snmptrap`. O `snmptrapd` é necessário somente no servidor ou proxy que receberá traps.

## 4. Validar o polling SNMP antes de importar o template

Substitua `COMMUNITY` e `AG561_IP`.

Verifique a descrição do equipamento:

```bash
snmpget -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.2.1.1.1.0
```

No firmware validado, o retorno esperado é semelhante a:

```text
Aligera AG561 8.16
```

Valide o ramo enterprise da Aligera:

```bash
snmpwalk -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.4.1.41933
```

Consultas úteis de capacidade:

```bash
snmpget -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.4.1.41933.1.2.1.0
snmpget -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.4.1.41933.1.3.1.0
snmpget -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.4.1.41933.1.4.1.0
```

Na configuração validada:

```text
Interfaces E1: 1
Entradas na tabela de canais: 31
Peers SIP: 1
```

As 31 entradas correspondem a 30 canais de voz MFCR2 mais a entrada de sinalização TS16 (`SIG`). O template exclui automaticamente `SIG(6)` do monitoramento de canais de voz.

## 5. Importar o template no Zabbix

No Zabbix 7.0:

1. Acesse **Data collection → Templates**.
2. Clique em **Import**.
3. Selecione `Aligera/7.0/template_aligera_ag561_e1_snmp.yaml`.
4. Revise as opções de importação.
5. Importe o template.

O template deve aparecer como:

```text
Aligera AG561 E1 by SNMP
```

Grupo:

```text
Templates/Network devices
```

## 6. Criar ou configurar o host AG561

Em **Data collection → Hosts**:

1. Crie o host ou abra um AG561 existente.
2. Adicione uma **interface SNMP**.
3. Configure o endereço IP do equipamento.
4. Configure a porta `161`.
5. Selecione **SNMPv2**.
6. Informe a mesma community configurada no equipamento.
7. Vincule o template **Aligera AG561 E1 by SNMP**.
8. Salve o host.

### Requisito importante para traps

O IP ou DNS selecionado na interface SNMP do host deve corresponder ao endereço de origem visto na trap recebida. O Zabbix associa traps aos hosts comparando o endereço da trap com a interface SNMP do host.

Se o AG561 enviar traps por um endereço de origem diferente daquele configurado na interface SNMP, os itens de trap podem não ser associados corretamente.

## 7. Macros de usuário

O template exporta 15 macros. Sobrescreva no nível do host somente quando a configuração real ou o baseline exigirem.

| Macro | Padrão | Recomendação |
|---|---:|---|
| `{$AG561.CHANNEL.NA.WARN}` | `1` | Mantenha `1` salvo se N/A for intencional em canais de voz. TS16/SIG já é excluído. |
| `{$AG561.CHANNEL.UTIL.HIGH}` | `90` | Limite High de utilização média em 5 minutos. |
| `{$AG561.CHANNEL.UTIL.WARN}` | `80` | Limite Warning de utilização média em 5 minutos. |
| `{$AG561.E1.EXPECTED}` | `1` | Ajuste para a quantidade real de interfaces E1. |
| `{$AG561.SIG.EXPECTED}` | `1` | A configuração validada possui uma entrada de sinalização. |
| `{$AG561.SIP.EXPECTED}` | `1` | Ajuste para a quantidade real de peers SIP. |
| `{$AG561.VOICE.EXPECTED}` | `30` | A configuração E1 validada possui 30 canais de voz. |
| `{$E1.CODE.RATE.WARN}` | `0` | `0` alerta em qualquer aumento. Calibre após observar baseline saudável. |
| `{$E1.CRC.RATE.WARN}` | `0` | `0` alerta em qualquer aumento. Calibre após observar baseline saudável. |
| `{$E1.SLIP.RATE.HIGH}` | `0.1` | Limite High persistente após 15 minutos. Calibre com histórico de produção. |
| `{$E1.SLIP.RATE.WARN}` | `0` | `0` alerta em qualquer aumento. |
| `{$ICMP.LOSS.WARN}` | `20` | Percentual médio de perda para Warning. |
| `{$ICMP.RESPONSE.WARN}` | `100` | Latência média em milissegundos para Warning. |
| `{$IF.DISCARD.RATE.WARN}` | `0` | `0` alerta em crescimento persistente de discards. |
| `{$IF.ERROR.RATE.WARN}` | `0` | `0` alerta em crescimento persistente de erros de interface. |

As macros `*.EXPECTED` também alimentam a trigger de divergência de configuração/capacidade.

## 8. Validar o polling após criar o host

Depois que o host estiver habilitado, consulte **Monitoring → Latest data**.

Confirme pelo menos:

- Descrição do sistema / firmware
- Uptime
- Disponibilidade SNMP
- ICMP disponibilidade/perda/latência
- Quantidade de E1 e estado de alarme
- Tempo das estatísticas E1
- CRC, slips e code violations
- Quantidade de canais
- Quantidade de peers SIP
- Interfaces Ethernet e tráfego RX/TX de 64 bits

A descoberta de baixo nível pode precisar de um ou mais ciclos antes que todos os itens protótipos apareçam.

### Descoberta esperada dos canais

Na configuração validada:

```text
Canal 1–15   = voz
Canal 16     = SIG, excluído do monitoramento de voz
Canal 17–31  = voz
```

O Honeycomb de status deve exibir 30 canais de voz.

## 9. Configurar recepção de SNMP traps

O template contém os seguintes itens de trap:

| Notificação | OID | Comportamento |
|---|---|---|
| `e1AlarmsChange` | `1.3.6.1.4.1.41933.1.2.3.1` | Evento informativo; polling continua sendo referência para o estado persistente da E1. |
| `chanStatusChange` | `1.3.6.1.4.1.41933.1.3.3.1` | Evento informativo; polling continua sendo referência para o estado persistente do canal. |
| `sipKeepaliveChange` | `1.3.6.1.4.1.41933.1.4.3.1` | Evento informativo. |
| Traps não reconhecidas | `snmptrap.fallback` | Armazena traps não casadas pelos itens específicos. |

As chaves específicas aceitam tanto o nome simbólico da notificação quanto o OID numérico. Portanto, a MIB da Aligera não é obrigatória para o matching. Ainda assim, instalá-la facilita diagnóstico manual e deixa a saída do Net-SNMP mais legível.

### 9.1 Habilitar o SNMP trapper do Zabbix

No Zabbix Server ou Proxy que receberá as traps, edite o arquivo correspondente:

```text
/etc/zabbix/zabbix_server.conf
```

ou:

```text
/etc/zabbix/zabbix_proxy.conf
```

Configure:

```ini
StartSNMPTrapper=1
SNMPTrapperFile=/var/lib/zabbix/snmptraps/snmptraps.log
```

Evite armazenar o arquivo em `/tmp` em sistemas onde o systemd utiliza `PrivateTmp`.

Crie o diretório:

```bash
mkdir -p /var/lib/zabbix/snmptraps
```

Garanta que a conta que executa o handler consiga gravar no arquivo/diretório e que o Zabbix Server/Proxy consiga lê-lo. Os usuários de serviço variam conforme a distribuição; valide localmente antes de aplicar `chown` fixo.

### 9.2 Instalar o handler Bash oficial do Zabbix

A documentação do Zabbix 7.0 disponibiliza um handler Bash. Baixe-o:

```bash
curl -L \
  -o /usr/sbin/zabbix_trap_handler.sh \
  https://raw.githubusercontent.com/zabbix/zabbix-docker/7.0/templates/scripts/snmptraps/zabbix_trap_handler.sh

chmod 755 /usr/sbin/zabbix_trap_handler.sh
```

Revise o script e garanta que o arquivo de saída seja o mesmo configurado no Zabbix:

```text
/var/lib/zabbix/snmptraps/snmptraps.log
```

### 9.3 Configurar o snmptrapd

Edite:

```text
/etc/snmp/snmptrapd.conf
```

Para SNMPv2c, substitua `TRAP_COMMUNITY` pela community configurada no AG561 para traps:

```conf
authCommunity log,execute,net TRAP_COMMUNITY
traphandle default /bin/bash /usr/sbin/zabbix_trap_handler.sh
```

A permissão `execute` é necessária para o `traphandle` executar o script.

Reinicie os serviços:

```bash
systemctl restart snmptrapd
systemctl restart zabbix-server
```

Se as traps forem processadas por um Zabbix Proxy:

```bash
systemctl restart zabbix-proxy
```

Verifique o status:

```bash
systemctl --no-pager --full status snmptrapd
systemctl --no-pager --full status zabbix-server
```

ou:

```bash
systemctl --no-pager --full status zabbix-proxy
```

Confirme que UDP/162 está em escuta:

```bash
ss -lunp | grep ':162'
```

## 10. Configurar traps no AG561

Em cada AG561 configure:

- Destino das traps: IP do Zabbix Server ou Proxy receptor
- Porta de destino: UDP `162`
- Versão SNMP: v2c
- Community de trap: a mesma aceita pelo `snmptrapd`
- Habilite as notificações necessárias para mudanças de estado de E1, canais e SIP

O caminho exato no menu pode variar conforme o firmware do AG561. O template não altera a configuração do equipamento.

No firewall, limite UDP/162 aos endereços de origem autorizados dos AG561.

## 11. Validar a recepção das traps

### Nível de rede

No receptor:

```bash
tcpdump -ni any udp port 162
```

Provoque uma mudança controlada no AG561 e confirme a chegada de pacote UDP/162 a partir do IP esperado do equipamento.

### Arquivo de traps

```bash
tail -f /var/lib/zabbix/snmptraps/snmptraps.log
```

Uma entrada corretamente formatada para o Zabbix contém uma linha com `ZBXTRAP` seguida do endereço do remetente.

Procure notificações Aligera:

```bash
grep -E 'e1AlarmsChange|chanStatusChange|sipKeepaliveChange|41933\.1\.(2\.3\.1|3\.3\.1|4\.3\.1)' \
  /var/lib/zabbix/snmptraps/snmptraps.log
```

### No Zabbix

Em **Monitoring → Latest data**, procure por:

- `SNMP trap: E1 alarm state changed`
- `SNMP trap: Channel status changed`
- `SNMP trap: SIP keepalive changed`
- `SNMP traps: Unmatched fallback`

Uma trap específica gera um evento INFO curto. A severidade e persistência da falha continuam determinadas pelas triggers de polling.

## 12. Troubleshooting

### Polling não funciona

Teste:

```bash
snmpget -v2c -c 'COMMUNITY' AG561_IP 1.3.6.1.2.1.1.1.0
```

Se falhar, verifique:

- Community
- Serviço SNMP no equipamento
- Firewall UDP/161
- Restrições de origem configuradas no AG561
- Roteamento

### Traps não chegam ao servidor

Execute:

```bash
tcpdump -ni any udp port 162
```

Se nenhum pacote chegar, verifique:

- Destino de traps no AG561
- Firewall UDP/162
- Versão/community das traps
- Roteamento

### Pacotes chegam, mas nada é gravado no arquivo

Verifique:

```bash
journalctl -u snmptrapd -n 100 --no-pager
cat /etc/snmp/snmptrapd.conf
ls -ld /var/lib/zabbix/snmptraps
ls -l /usr/sbin/zabbix_trap_handler.sh
```

Confira `authCommunity`, `traphandle`, permissões do script e permissões do arquivo/diretório.

### Arquivo recebe traps, mas o Zabbix não recebe

Verifique:

```bash
grep -E '^(StartSNMPTrapper|SNMPTrapperFile)=' /etc/zabbix/zabbix_server.conf
```

ou o arquivo do proxy.

Confirme:

- `StartSNMPTrapper=1`
- `SNMPTrapperFile` coincide exatamente com o arquivo gerado pelo handler
- Zabbix consegue ler o arquivo
- Zabbix foi reiniciado após as alterações
- O host possui interface SNMP
- O IP/DNS selecionado na interface SNMP corresponde ao endereço de origem da trap

O último item é crítico: antes de avaliar as expressões `snmptrap[]`, o Zabbix identifica os hosts candidatos pelo endereço de origem da trap.

### Trap aparece somente no fallback

Se uma notificação Aligera cair em `snmptrap.fallback`, examine o valor bruto em Latest data e confirme se contém o nome simbólico ou o OID numérico esperado.

OIDs esperados:

```text
E1:      1.3.6.1.4.1.41933.1.2.3.1
Canal:   1.3.6.1.4.1.41933.1.3.3.1
SIP:     1.3.6.1.4.1.41933.1.4.3.1
```

## 13. Instalação opcional da MIB Aligera

Os OIDs de polling no template são numéricos e as chaves de traps também aceitam os OIDs numéricos. Portanto, a MIB não é obrigatória para o funcionamento normal.

Ainda assim, a instalação é recomendada para `snmpwalk`, `snmptranslate` e saída de traps mais legível. Instale a MIB Aligera conforme o diretório/configuração de MIBs do Net-SNMP da sua distribuição e valide:

```bash
snmptranslate -On e1AlarmsChange
snmptranslate -On chanStatusChange
snmptranslate -On sipKeepaliveChange
```

## 14. Recomendações de segurança

- Não utilize a community padrão `public`.
- Use communities dedicadas para polling read-only e traps quando o equipamento permitir.
- Restrinja UDP/161 aos IPs do Zabbix Server/Proxy.
- Restrinja UDP/162 aos IPs dos AG561.
- Mantenha SNMPv2c somente em redes privadas/confiáveis.
- Não exponha UDP/161 ou UDP/162 diretamente à Internet.
- Se uma futura versão de firmware suportar SNMPv3 para o conjunto de recursos necessário, prefira autenticação e criptografia.

## 15. Checklist de validação operacional

Após a instalação confirme:

- [ ] `sysDescr` mostra modelo/firmware esperado.
- [ ] Disponibilidade SNMP está OK.
- [ ] Dados ICMP estão sendo coletados.
- [ ] Uma E1 foi descoberta ou `{$AG561.E1.EXPECTED}` foi ajustada.
- [ ] 30 canais de voz foram descobertos ou `{$AG561.VOICE.EXPECTED}` foi ajustada.
- [ ] TS16/SIG não aparece no Honeycomb de voz.
- [ ] Quantidade de peers SIP coincide com `{$AG561.SIP.EXPECTED}`.
- [ ] Interfaces Ethernet são descobertas por `ifType=6`.
- [ ] Contadores de tráfego de 64 bits estão atualizando.
- [ ] Contadores/taxas de qualidade E1 estão atualizando.
- [ ] Trigger de divergência de capacidade está OK.
- [ ] UDP/162 chega ao Zabbix Server/Proxy correto.
- [ ] Traps Aligera são gravadas no arquivo de traps.
- [ ] Itens específicos recebem as notificações correspondentes.
- [ ] `snmptrap.fallback` está disponível para diagnóstico.
- [ ] Macros de threshold foram revisadas após um período representativo de baseline.

## Referências

- Documentação Zabbix 7.0 sobre SNMP traps: https://www.zabbix.com/documentation/7.0/pt/manual/config/items/itemtypes/snmptrap
- Documentação Zabbix 7.0 sobre monitoramento SNMP: https://www.zabbix.com/documentation/7.0/pt/manual/config/items/itemtypes/snmp
- Trabalho original AG562 de Douglas Boldrini: https://github.com/boldrinidouglas/ZBX-GRA-ALIGERA
