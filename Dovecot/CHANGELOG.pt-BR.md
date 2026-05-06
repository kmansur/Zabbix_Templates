# Changelog

English version: [CHANGELOG.md](CHANGELOG.md)

Todas as alteracoes relevantes deste projeto sao documentadas aqui.

Manutencao da documentacao: quando este changelog em portugues for atualizado, atualize tambem o `CHANGELOG.md`.

## 2.0.0 - Unreleased

### Adicionado

- Adicionado `Template_Dovecot_7.0.yaml` para Zabbix 7.0.
- Adicionado item master `dovecot.stats` em JSON com itens dependentes.
- Adicionadas macros de habilitacao e portas para IMAP, IMAPS, POP3 e POP3S.
- Adicionadas macros de recovery para triggers de conexoes IMAP e POP3.
- Adicionado monitoramento `proc.num[{$DOVECOT.PROCESS.NAME}]` para processo master do Dovecot.
- Adicionadas macros de arquivos de configuracao para checksum.
- Adicionados itens de saude do coletor e ultimo erro.
- Adicionada trigger de ausencia de dados para o item master `dovecot.stats`.
- Adicionadas triggers de warning e high para total de conexoes com macros de recovery.
- Adicionados itens de tempo de resposta TCP e trigger de warning para IMAP, IMAPS, POP3 e POP3S.
- Adicionado mapa de valor de estado de servico.
- Adicionados graficos `Dovecot connections` e `Dovecot service response time`.
- Adicionada documentacao de validacao e testes locais do parser.
- Adicionados arquivos de contribuicao, seguranca e licenca.

### Alterado

- Atualizado `dovecot_stats.sh` para usar `doveadm who -1` e retornar JSON valido.
- Atualizados scripts legados IMAP e POP3 para usar `doveadm who -1` com correspondencia mais restrita do token de protocolo.
- Atualizadas triggers de disponibilidade para exigir falha durante janela completa de 3 minutos.
- Atualizadas triggers de conexao para usar recovery expressions e macros de recovery.
- Atualizados nomes das triggers para iniciar com `PROBLEM`, `WARNING` ou `INFO`.
- Atualizados UserParameters para chamar scripts com `sudo -n`.
- Movidos o template XML Zabbix 5.0, contadores IMAP/POP3 legados e UserParameter legado para `legacy/zabbix-5.0/`.
- Reduzido o `userparameter_dovecot.conf` principal para as chaves Zabbix 7.0 usadas pelo template atual.
- Atualizada documentacao em ingles e portugues para o fluxo 2.0.0.

### Preservado

- Mantido `legacy/zabbix-5.0/Template_App_Dovecot.xml` como template legado Zabbix 5.0 da versao 1.0.0.
- Mantidos UserParameters legados `dovecot.imap` e `dovecot.pop` em `legacy/zabbix-5.0/userparameter_dovecot_legacy.conf`.

## 1.0.0 - 2026-05-03

### Adicionado

- Adicionados arquivos README em ingles e portugues.
- Adicionados changelogs em ingles e portugues.

### Alterado

- Marcada a versao atual em producao como `1.0.0`.
- Reorganizada a estrutura do projeto.

### Preservado

- Preservado o comportamento do template XML Zabbix 5.0.
- Preservados scripts existentes de sessoes do Dovecot.
- Preservadas definicoes existentes de UserParameter.
