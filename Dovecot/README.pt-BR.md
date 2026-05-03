# Template Zabbix Dovecot

English version: [README.md](README.md)

> Versao de producao: 1.0.0
>
> Manutencao da documentacao: quando este README em portugues for atualizado,
> atualize tambem o `README.md` na mesma alteracao.

Projeto de template Zabbix para monitoramento basico do Dovecot. Esta versao e
baseada em um ambiente de producao usando caminhos de FreeBSD e formato de
template Zabbix 5.0.

## Arquivos

- `Template_App_Dovecot.xml`: export do template Zabbix.
- `dovecot_num_imap.sh`: conta sessoes IMAP ativas usando `doveadm who`.
- `dovecot_num_pop.sh`: conta sessoes POP3 ativas usando `doveadm who`.
- `dovecot_stats.sh`: retorna contadores de IMAP, POP3 e total em CSV.
- `userparameter_dovecot.conf`: definicoes de UserParameter do Zabbix agent.
- `CHANGELOG.md`: changelog em ingles.
- `CHANGELOG.pt-BR.md`: changelog em portugues.

## Dados Monitorados

- Conexoes IMAP ativas.
- Conexoes POP3 ativas.
- Versao do Dovecot.
- Disponibilidade do servico IMAP.
- Disponibilidade do servico POP3.
- Disponibilidade do servico IMAPS na porta TCP 993.
- Disponibilidade do servico POP3S na porta TCP 995.
- Alteracoes de checksum em arquivos selecionados de configuracao do Dovecot.

## Requisitos

- Zabbix server compativel com export de template versao 5.0.
- Zabbix agent instalado no host Dovecot.
- Dovecot instalado com `doveadm` disponivel.
- Caminhos no padrao FreeBSD, salvo ajustes manuais.
- Acesso via `sudo` para o usuario do Zabbix agent executar os scripts de
  sessoes do Dovecot.

Caminhos padrao usados por esta versao:

```text
/usr/local/bin/doveadm
/usr/local/sbin/dovecot
/usr/local/scripts/
/usr/local/etc/dovecot/
```

Para Linux ou outros sistemas operacionais, ajuste os caminhos dos scripts, os
UserParameters e os itens de checksum de arquivos de configuracao conforme
necessario.

## Instalacao

1. Copie os scripts para o host monitorado:

   ```bash
   cp dovecot_num_imap.sh /usr/local/scripts/
   cp dovecot_num_pop.sh /usr/local/scripts/
   cp dovecot_stats.sh /usr/local/scripts/
   chmod 755 /usr/local/scripts/dovecot_num_imap.sh
   chmod 755 /usr/local/scripts/dovecot_num_pop.sh
   chmod 755 /usr/local/scripts/dovecot_stats.sh
   ```

2. Copie o arquivo de UserParameter para o diretorio de include do Zabbix agent:

   ```bash
   cp userparameter_dovecot.conf /usr/local/etc/zabbix_agentd.conf.d/
   ```

3. Configure o `sudo` para o usuario do Zabbix agent conforme a politica de
   seguranca local. Os UserParameters atuais chamam os scripts de sessao usando
   `sudo`.

4. Reinicie o Zabbix agent.

5. Importe `Template_App_Dovecot.xml` no Zabbix.

6. Vincule `Template App Dovecot` ao host Dovecot.

## Macros Do Template

| Macro | Padrao | Descricao |
| --- | ---: | --- |
| `{$IMAP.WARN}` | `200` | Limite de warning para conexoes IMAP ativas. |
| `{$IMAP.HIGH}` | `350` | Limite alto para conexoes IMAP ativas. |
| `{$POP.WARN}` | `200` | Limite de warning para conexoes POP3 ativas. |
| `{$POP.HIGH}` | `350` | Limite alto para conexoes POP3 ativas. |

Ajuste estas macros por host ou grupo de hosts conforme a carga esperada.

## Observacoes

- Esta versao 1.0.0 preserva intencionalmente o comportamento em producao do
  template e dos scripts existentes.
- A estrutura do repositorio foi reorganizada para deixar template, scripts,
  arquivo de UserParameter, READMEs e changelogs no mesmo diretorio.
- Versoes futuras podem modernizar o metodo de coleta, triggers, macros e
  formato do template.
