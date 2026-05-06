# Template Zabbix Courier-IMAP

English version: [README.md](README.md)

> Versao de desenvolvimento: 1.2.0
>
> Status do projeto: manutencao apenas. Este template nao esta mais em desenvolvimento ativo.
>
> Manutencao da documentacao: quando este README em portugues for atualizado, atualize tambem o `README.md`.

Projeto de template Zabbix para monitorar logins Courier-IMAP e Courier-POP3 em FreeBSD por UserParameters do Zabbix agent. A versao 1.2.0 adiciona o export YAML para Zabbix 7.0 como template atual e mantem o export XML original para Zabbix 3.2 em ambientes legados.

## Arquivos

- `templates/7.0/Template_Courier_IMAP_7.0.yaml`: export atual do template Zabbix 7.0.
- `templates/3.2/Template_Courier_IMAP_3.2.xml`: export XML legado para Zabbix 3.2.
- `scripts/courier_imapd.sh`: conta eventos de login IMAP do minuto anterior.
- `scripts/courier_imapd-ssl.sh`: conta eventos de login IMAPS do minuto anterior.
- `scripts/courier_pop3d.sh`: conta eventos de login POP3 do minuto anterior.
- `scripts/courier_pop3d-ssl.sh`: conta eventos de login POP3S do minuto anterior.
- `agent/userparameter_courier.conf`: UserParameters do Zabbix agent.
- `docs/VALIDATION.md`: checklist de validacao.
- `LICENSE`: licenca MIT.
- `CHANGELOG.md`: changelog em ingles.
- `CHANGELOG.pt-BR.md`: changelog em portugues.

## Dados Monitorados

- Eventos de login IMAP por minuto.
- Eventos de login IMAPS por minuto.
- Eventos de login POP3 por minuto.
- Eventos de login POP3S por minuto.
- Eventos de log de limite maximo de conexoes ativas do Courier-IMAP.
- Eventos de log de limite maximo de conexoes por IP do Courier-IMAP.
- Alteracoes de checksum em arquivos de configuracao Courier-IMAP e maildrop.

## Requisitos

- Zabbix server compativel com export de template 7.0.
- Zabbix agent instalado no host Courier-IMAP.
- Host FreeBSD com Courier-IMAP/Courier-POP3 gravando em `/var/log/maillog`.
- Usuario do Zabbix agent com permissao de leitura em `/var/log/maillog`.
- Shell POSIX e `date` do FreeBSD com suporte a `-j -v-1M`.

Caminhos padrao:

```text
/usr/local/scripts/
/usr/local/etc/courier-imap/
/usr/local/etc/maildroprc
/var/log/maillog
```

Os scripts aceitam `COURIER_MAILLOG` para sobrescrever o caminho do log de email. O gerenciador do servico ou politicas restritas de execucao do agent podem nao preservar variaveis de ambiente.

## Instalacao

1. Copie os scripts de `scripts/` para `/usr/local/scripts/` e aplique modo `755`.
2. Restrinja o dono dos scripts:

   ```bash
   chown root:wheel /usr/local/scripts/courier_imapd.sh
   chown root:wheel /usr/local/scripts/courier_imapd-ssl.sh
   chown root:wheel /usr/local/scripts/courier_pop3d.sh
   chown root:wheel /usr/local/scripts/courier_pop3d-ssl.sh
   ```

3. Copie `agent/userparameter_courier.conf` para o diretorio de include do Zabbix agent.
4. Confirme que o Zabbix agent consegue ler `/var/log/maillog`.
5. Reinicie o Zabbix agent.
6. Importe `templates/7.0/Template_Courier_IMAP_7.0.yaml` no Zabbix 7.0.
7. Vincule `Template App MAIL Courier-IMAP` ao host Courier-IMAP.

## Validacao

```bash
sh -n /usr/local/scripts/courier_imapd.sh
sh -n /usr/local/scripts/courier_imapd-ssl.sh
sh -n /usr/local/scripts/courier_pop3d.sh
sh -n /usr/local/scripts/courier_pop3d-ssl.sh
sudo -u zabbix zabbix_agentd -t imapd
sudo -u zabbix zabbix_agentd -t imapd-ssl
sudo -u zabbix zabbix_agentd -t pop3d
sudo -u zabbix zabbix_agentd -t pop3d-ssl
```

Mais validacoes estao em `docs/VALIDATION.md`.

## Metodo De Contagem

Os quatro scripts contam registros `LOGIN` em `/var/log/maillog` que batem com o minuto anterior e com o nome do servico Courier. Os scripts IMAP e POP3 sem TLS excluem as variantes SSL para evitar contagem duplicada.

## Notas De Compatibilidade

- `templates/7.0/Template_Courier_IMAP_7.0.yaml` e o template atual para Zabbix 7.0.
- `templates/3.2/Template_Courier_IMAP_3.2.xml` foi preservado como export legado para ambientes Zabbix 3.2.
- As chaves dos itens continuam `imapd`, `imapd-ssl`, `pop3d` e `pop3d-ssl` para nao quebrar hosts existentes.
- As triggers de log continuam usando `/var/log/maillog` diretamente no template Zabbix.
- Os scripts sao orientados a FreeBSD porque dependem da sintaxe do `date` do FreeBSD. Valide antes de adaptar para Linux.

## Licenca

Este projeto e licenciado sob a MIT License. Veja `LICENSE`.
