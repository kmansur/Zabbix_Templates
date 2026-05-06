# Changelog

## 1.2.0 - 2026-05-06

- Adicionado o export YAML Zabbix 7.0 em `templates/7.0/Template_Courier_IMAP_7.0.yaml`.
- Adicionada documentacao do template Zabbix 7.0.
- Atualizados README e validacao para tratar o export Zabbix 7.0 como template atual.
- Mantido o export XML Zabbix 3.2 documentado como legado.

## 1.1.0 - 2026-05-06

- Reorganizado o projeto nos diretorios atuais do repositorio: `templates/3.2`, `scripts`, `agent` e `docs`.
- Movido o export XML legado Zabbix 3.2 para `templates/3.2/Template_Courier_IMAP_3.2.xml`.
- Movidos os scripts de coleta Courier para `scripts/` e os UserParameters para `agent/`.
- Atualizados os UserParameters para usar `/usr/local/scripts/`.
- Adicionados READMEs em ingles e portugues.
- Adicionada a licenca MIT.
- Adicionada documentacao de validacao.
- Corrigidos pequenos problemas de texto no XML legado em nomes de graficos, descricoes de triggers e caminhos de configuracao exibidos.
- Evitada contagem duplicada de logins SSL nos scripts IMAP e POP3 sem TLS.

## 1.0.0 - 2017-04-26

- Export XML inicial do template Courier-IMAP para Zabbix 3.2.
