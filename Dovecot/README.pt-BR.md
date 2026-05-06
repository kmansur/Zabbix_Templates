# Template Zabbix Dovecot

English version: [README.md](README.md)

> Versao de desenvolvimento: 2.0.0
>
> Manutencao da documentacao: quando este README em portugues for atualizado, atualize tambem o `README.md`.

Projeto de template Zabbix para monitorar Dovecot por UserParameters do Zabbix agent. A versao 2.0.0 adiciona template YAML para Zabbix 7.0, coleta em JSON, itens dependentes, macros de servico, macros de porta, macros de recovery, monitoramento de processo, tempo de resposta dos servicos, mapa de valores, graficos e documentacao de validacao. O XML legado 1.0.0 foi mantido como referencia.

## Arquivos

- `templates/7.0/Template_Dovecot_7.0.yaml`: export atual do template Zabbix 7.0 da versao 2.0.0.
- `templates/6.0/`: reservado para um export futuro compativel com Zabbix 6.0.
- `templates/8.0/Template_Dovecot_8.0.yaml`: export do template Zabbix 8.0, validado estaticamente e pronto para teste de importacao.
- `dovecot_stats.sh`: script principal de coleta em JSON.
- `userparameter_dovecot.conf`: UserParameters do Zabbix agent.
- `legacy/zabbix-5.0/`: template XML legado Zabbix 5.0, contadores IMAP/POP3 legados e UserParameter correspondente.
- `docs/VALIDATION.md`: checklist de validacao.
- `tests/test_dovecot_stats.sh`: teste local do parser.
- `CHANGELOG.md` e `CHANGELOG.pt-BR.md`: changelogs.

## Dados Monitorados

- Disponibilidade do coletor Dovecot e ultimo erro.
- Conexoes IMAP ativas.
- Conexoes POP3 ativas.
- Total de conexoes IMAP e POP3 ativas.
- Quantidade de processos master do Dovecot.
- Versao do Dovecot.
- Disponibilidade TCP dos servicos IMAP, IMAPS, POP3 e POP3S.
- Tempo de resposta TCP dos servicos IMAP, IMAPS, POP3 e POP3S.
- Alteracao de checksum em arquivos de configuracao do Dovecot.

## Requisitos

- Zabbix server compativel com export de template 7.0.
- Zabbix agent instalado no host Dovecot.
- Dovecot instalado com `doveadm` disponivel.
- `sudo` para o usuario do Zabbix agent executar os scripts de sessoes.

Caminhos padrao:

```text
/usr/local/bin/doveadm
/usr/local/sbin/dovecot
/usr/local/scripts/
/usr/local/etc/dovecot/
```

Os scripts aceitam `DOVECOT_DOVEADM` para sobrescrever o caminho do `doveadm`. Com `sudo -n`, o sudoers pode nao preservar variaveis de ambiente.

## Instalacao

1. Copie `dovecot_stats.sh` para `/usr/local/scripts/` e aplique modo `755`.
2. Restrinja o dono dos scripts:

   ```bash
   # FreeBSD
   chown root:wheel /usr/local/scripts/dovecot_stats.sh

   # Linux
   chown root:root /usr/local/scripts/dovecot_stats.sh
   ```

3. Copie `userparameter_dovecot.conf` para o diretorio de include do Zabbix agent.
4. Configure sudoers:

   ```text
   zabbix ALL=(root) NOPASSWD: /usr/local/scripts/dovecot_stats.sh
   ```

5. Reinicie o Zabbix agent.
6. Importe `templates/7.0/Template_Dovecot_7.0.yaml` no Zabbix 7.0.
7. Vincule `Template App Dovecot` ao host Dovecot.

## Validacao

```bash
sh -n /usr/local/scripts/dovecot_stats.sh
sudo -u zabbix sudo -n /usr/local/scripts/dovecot_stats.sh
sudo -u zabbix zabbix_agentd -t dovecot.stats
sudo -u zabbix zabbix_agentd -t dovecot.version
```

Mais validacoes estao em `docs/VALIDATION.md`.

## Saida Do Script

```json
{"status":1,"imap":10,"pop3":2,"total":12,"error":""}
```

Em falha:

```json
{"status":0,"imap":0,"pop3":0,"total":0,"error":"doveadm_who_failed"}
```

## Metodo De Contagem

A versao 2.0.0 usa:

```bash
doveadm who -1
```

Isso evita subcontagem quando `doveadm who` agrupa varias conexoes do mesmo usuario em uma unica linha.

## Macros Do Template

| Macro | Padrao | Descricao |
| --- | ---: | --- |
| `{$DOVECOT.IMAP.CONN.WARN}` | `200` | Limite de warning para media de conexoes IMAP. |
| `{$DOVECOT.IMAP.CONN.WARN.RECOVERY}` | `180` | Recovery do warning IMAP. |
| `{$DOVECOT.IMAP.CONN.HIGH}` | `350` | Limite high para media de conexoes IMAP. |
| `{$DOVECOT.IMAP.CONN.HIGH.RECOVERY}` | `320` | Recovery do high IMAP. |
| `{$DOVECOT.POP3.CONN.WARN}` | `200` | Limite de warning para media de conexoes POP3. |
| `{$DOVECOT.POP3.CONN.WARN.RECOVERY}` | `180` | Recovery do warning POP3. |
| `{$DOVECOT.POP3.CONN.HIGH}` | `350` | Limite high para media de conexoes POP3. |
| `{$DOVECOT.POP3.CONN.HIGH.RECOVERY}` | `320` | Recovery do high POP3. |
| `{$DOVECOT.TOTAL.CONN.WARN}` | `350` | Limite de warning para media total de conexoes IMAP e POP3. |
| `{$DOVECOT.TOTAL.CONN.WARN.RECOVERY}` | `320` | Recovery do warning total de conexoes. |
| `{$DOVECOT.TOTAL.CONN.HIGH}` | `600` | Limite high para media total de conexoes IMAP e POP3. |
| `{$DOVECOT.TOTAL.CONN.HIGH.RECOVERY}` | `550` | Recovery do high total de conexoes. |
| `{$DOVECOT.SERVICE.RESPONSE.WARN}` | `2` | Limite de warning em segundos para tempo de resposta TCP. |
| `{$DOVECOT.IMAP.ENABLED}` | `1` | Defina `0` para desabilitar trigger IMAP. |
| `{$DOVECOT.IMAPS.ENABLED}` | `1` | Defina `0` para desabilitar trigger IMAPS. |
| `{$DOVECOT.POP3.ENABLED}` | `1` | Defina `0` para desabilitar trigger POP3. |
| `{$DOVECOT.POP3S.ENABLED}` | `1` | Defina `0` para desabilitar trigger POP3S. |
| `{$DOVECOT.IMAP.PORT}` | `143` | Porta TCP IMAP. |
| `{$DOVECOT.IMAPS.PORT}` | `993` | Porta TCP IMAPS. |
| `{$DOVECOT.POP3.PORT}` | `110` | Porta TCP POP3. |
| `{$DOVECOT.POP3S.PORT}` | `995` | Porta TCP POP3S. |
| `{$DOVECOT.PROCESS.NAME}` | `dovecot` | Processo master usado por `proc.num[]`. |
| `{$DOVECOT.CONF.FILE}` | `/usr/local/etc/dovecot/dovecot.conf` | Arquivo principal para checksum. |
| `{$DOVECOT.SQL.CONF.FILE}` | `/usr/local/etc/dovecot/dovecot-mysql.conf` | Arquivo SQL auth para checksum. |

## Notas De Compatibilidade

- `templates/7.0/Template_Dovecot_7.0.yaml` e o template principal da versao 2.0.0.
- `templates/6.0/` e um placeholder ate que um export Zabbix 6.0 seja validado.
- `templates/8.0/Template_Dovecot_8.0.yaml` esta disponivel para teste de importacao no Zabbix 8.0; valide em homologacao antes do uso em producao.
- `legacy/zabbix-5.0/Template_App_Dovecot.xml` foi mantido como template legado 1.0.0.
- `legacy/zabbix-5.0/dovecot_num_imap.sh`, `legacy/zabbix-5.0/dovecot_num_pop.sh` e `legacy/zabbix-5.0/userparameter_dovecot_legacy.conf` preservam as chaves `dovecot.imap` e `dovecot.pop` para ambientes Zabbix 5.0.
- IMAPS e POP3S validam apenas conectividade TCP, nao negociacao TLS nem autenticacao.
