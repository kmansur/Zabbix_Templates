# Changelog

English version: [CHANGELOG.md](CHANGELOG.md)

Todas as alteracoes relevantes deste projeto sao documentadas aqui.

Manutencao da documentacao: quando este changelog em portugues for atualizado,
atualize tambem o `CHANGELOG.md` na mesma alteracao.

## 2.0.0 - Unreleased

### Adicionado

- Adicionado `Template_Dovecot_7.0.yaml` para Zabbix 7.0.
- Adicionado desenho de item master `dovecot.stats` baseado em JSON, com itens
  dependentes para status do coletor, conexoes IMAP, conexoes POP3 e total de
  conexoes.
- Adicionadas macros para habilitar triggers de disponibilidade de IMAP, IMAPS,
  POP3 e POP3S.
- Adicionadas macros de portas para verificacoes de servico IMAP, IMAPS, POP3 e
  POP3S.
- Adicionadas macros de caminho de arquivos de configuracao para monitoramento
  de checksum.
- Adicionados itens de saude do coletor e ultimo erro.

### Alterado

- Atualizado `dovecot_stats.sh` para retornar JSON valido em vez de CSV.
- Atualizados os scripts legados de contagem IMAP e POP3 com correspondencia de
  protocolo mais restrita.
- Atualizados os UserParameters para chamar os scripts de sessao com `sudo -n`.
- Atualizada a documentacao em ingles e portugues para o fluxo da versao 2.0.0.

### Preservado

- Mantido `Template_App_Dovecot.xml` como template legado Zabbix 5.0 da versao
  1.0.0.
- Mantidos os UserParameters `dovecot.imap` e `dovecot.pop` para
  compatibilidade.

## 1.0.0 - 2026-05-03

### Adicionado

- Adicionados arquivos README em ingles e portugues para o projeto do template
  Dovecot.
- Adicionados arquivos de changelog em ingles e portugues.

### Alterado

- Marcada a versao atual em producao do template Dovecot como `1.0.0`.
- Reorganizada a estrutura do projeto Dovecot para deixar template, scripts e
  configuracao de UserParameter no mesmo diretorio.

### Preservado

- Preservado o comportamento existente do template XML Zabbix 5.0.
- Preservados os scripts existentes de sessoes do Dovecot.
- Preservadas as definicoes existentes de UserParameter do Zabbix agent.
