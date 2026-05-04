# Template Zabbix Dovecot

English version: [README.md](README.md)

> Versao de desenvolvimento: 2.0.0
>
> Manutencao da documentacao: quando este README em portugues for atualizado,
> atualize tambem o `README.md` na mesma alteracao.

Projeto de template Zabbix para monitorar Dovecot por meio de UserParameters do
Zabbix agent. A versao 2.0.0 adiciona um template YAML para Zabbix 7.0, coleta
em JSON, itens dependentes, macros para habilitar servicos, macros de portas e
documentacao melhorada, mantendo o template XML 1.0.0 disponivel como
referencia.

## Arquivos

- `Template_Dovecot_7.0.yaml`: export do template Zabbix 7.0 da versao 2.0.0.
- `Template_App_Dovecot.xml`: template XML legado Zabbix 5.0 da versao 1.0.0.
- `dovecot_stats.sh`: script principal de coleta em JSON para sessoes Dovecot.
- `dovecot_num_imap.sh`: contador de sessoes IMAP mantido para compatibilidade.
- `dovecot_num_pop.sh`: contador de sessoes POP3 mantido para compatibilidade.
- `userparameter_dovecot.conf`: definicoes de UserParameter do Zabbix agent.
- `CHANGELOG.md`: changelog em ingles.
- `CHANGELOG.pt-BR.md`: changelog em portugues.

## Dados Monitorados

- Disponibilidade do coletor Dovecot e ultimo erro.
- Conexoes IMAP ativas.
- Conexoes POP3 ativas.
- Total de conexoes IMAP e POP3 ativas.
- Versao do Dovecot.
- Disponibilidade do servico IMAP.
- Disponibilidade do servico IMAPS.
- Disponibilidade do servico POP3.
- Disponibilidade do servico POP3S.
- Alteracoes de checksum em arquivos selecionados de configuracao do Dovecot.

## Requisitos

- Zabbix server compativel com export de template versao 7.0.
- Zabbix agent instalado no host Dovecot.
- Dovecot instalado com `doveadm` disponivel.
- Acesso via `sudo` para o usuario do Zabbix agent executar o script de sessoes
  do Dovecot.

Caminhos padrao usados por esta versao:

```text
/usr/local/bin/doveadm
/usr/local/sbin/dovecot
/usr/local/scripts/
/usr/local/etc/dovecot/
```

Os scripts suportam `DOVECOT_DOVEADM` como variavel de ambiente para sobrescrever
o caminho do `doveadm`. Para Linux ou outros sistemas operacionais, ajuste os
caminhos dos scripts, UserParameters e macros de arquivos de configuracao
conforme necessario.

## Instalacao

1. Copie os scripts para o host monitorado:

   ```bash
   cp dovecot_stats.sh /usr/local/scripts/
   cp dovecot_num_imap.sh /usr/local/scripts/
   cp dovecot_num_pop.sh /usr/local/scripts/
   chmod 755 /usr/local/scripts/dovecot_stats.sh
   chmod 755 /usr/local/scripts/dovecot_num_imap.sh
   chmod 755 /usr/local/scripts/dovecot_num_pop.sh
   ```

2. Copie o arquivo de UserParameter para o diretorio de include do Zabbix agent:

   ```bash
   cp userparameter_dovecot.conf /usr/local/etc/zabbix_agentd.conf.d/
   ```

3. Configure o `sudo` para o usuario do Zabbix agent. Os UserParameters usam
   `sudo -n`, entao permissoes ausentes falham rapidamente em vez de aguardar
   uma senha.

   Exemplo de regra sudoers:

   ```text
   zabbix ALL=(root) NOPASSWD: /usr/local/scripts/dovecot_stats.sh, /usr/local/scripts/dovecot_num_imap.sh, /usr/local/scripts/dovecot_num_pop.sh
   ```

4. Reinicie o Zabbix agent.

5. Importe `Template_Dovecot_7.0.yaml` no Zabbix 7.0.

6. Vincule `Template App Dovecot` ao host Dovecot.

## Saida Do Script

`dovecot_stats.sh` retorna JSON para o item master do Zabbix:

```json
{"status":1,"imap":10,"pop3":2,"total":12,"error":""}
```

Se a coleta falhar, o script ainda retorna JSON valido:

```json
{"status":0,"imap":0,"pop3":0,"total":0,"error":"doveadm_who_failed"}
```

## Macros Do Template

| Macro | Padrao | Descricao |
| --- | ---: | --- |
| `{$DOVECOT.IMAP.CONN.WARN}` | `200` | Limite de warning para media de conexoes IMAP ativas. |
| `{$DOVECOT.IMAP.CONN.HIGH}` | `350` | Limite alto para media de conexoes IMAP ativas. |
| `{$DOVECOT.POP3.CONN.WARN}` | `200` | Limite de warning para media de conexoes POP3 ativas. |
| `{$DOVECOT.POP3.CONN.HIGH}` | `350` | Limite alto para media de conexoes POP3 ativas. |
| `{$DOVECOT.IMAP.ENABLED}` | `1` | Defina como `0` para desabilitar triggers de disponibilidade IMAP. |
| `{$DOVECOT.IMAPS.ENABLED}` | `1` | Defina como `0` para desabilitar triggers de disponibilidade IMAPS. |
| `{$DOVECOT.POP3.ENABLED}` | `1` | Defina como `0` para desabilitar triggers de disponibilidade POP3. |
| `{$DOVECOT.POP3S.ENABLED}` | `1` | Defina como `0` para desabilitar triggers de disponibilidade POP3S. |
| `{$DOVECOT.IMAP.PORT}` | `143` | Porta TCP do IMAP. |
| `{$DOVECOT.IMAPS.PORT}` | `993` | Porta TCP do IMAPS. |
| `{$DOVECOT.POP3.PORT}` | `110` | Porta TCP do POP3. |
| `{$DOVECOT.POP3S.PORT}` | `995` | Porta TCP do POP3S. |
| `{$DOVECOT.CONF.FILE}` | `/usr/local/etc/dovecot/dovecot.conf` | Arquivo principal de configuracao Dovecot para checksum. |
| `{$DOVECOT.SQL.CONF.FILE}` | `/usr/local/etc/dovecot/dovecot-mysql.conf` | Arquivo de configuracao SQL de autenticacao para checksum. |

## Notas De Compatibilidade

- `Template_Dovecot_7.0.yaml` e o template principal da versao 2.0.0.
- `Template_App_Dovecot.xml` foi mantido como template legado da versao 1.0.0.
- Os UserParameters `dovecot.imap` e `dovecot.pop` foram preservados para
  compatibilidade.
- Novos itens do Zabbix 7.0 devem usar `dovecot.stats` como item master.
