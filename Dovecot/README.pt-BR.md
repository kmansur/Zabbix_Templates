# Template Zabbix para Dovecot

English version: [README.md](README.md)

> Versão em desenvolvimento: 3.0.0
>
> Status: branch de desenvolvimento. Valide em homologação antes de produção.
>
> Manutenção da documentação: quando este README em português for alterado, atualize também README.md na mesma mudança.

Projeto de template Zabbix para monitorar Dovecot usando um pequeno coletor POSIX shell e UserParameters do Zabbix agent. A versão 3.0.0 preserva as métricas existentes e, sempre que possível, as mesmas keys e UUIDs, melhorando separação de privilégios, portabilidade, validação de protocolo, testes de regressão e visibilidade operacional.

## Objetivos do projeto

- Preservar as métricas e identificadores existentes do template.
- Manter o coletor pequeno, auditável, compatível com POSIX shell e sem dependências de produção.
- Executar o coletor como o usuário não privilegiado do Zabbix agent.
- Elevar privilégio apenas para o comando exato e somente leitura doveadm who -1 quando o socket anvil exigir.
- Usar uma única coleta JSON com itens dependentes.
- Não armazenar usernames ou endereços no Zabbix.
- Suportar os caminhos comuns de Dovecot em FreeBSD e Linux.
- Manter os exports Zabbix 7.0 e 8.0 alinhados.

## Estrutura do repositório

- templates/7.0/Template_Dovecot_7.0.yaml - export para Zabbix 7.0.
- templates/8.0/Template_Dovecot_8.0.yaml - export para Zabbix 8.0.
- templates/6.0/ - reservado para um futuro export 6.0 validado.
- scripts/dovecot_stats.sh - coletor JSON atual.
- agent/userparameter_dovecot.conf - configuração atual de UserParameter.
- agent/sudoers.d/ - exemplos de sudoers com privilégio mínimo para FreeBSD e Linux.
- docs/VALIDATION.md - validações estáticas, no host, importação e produção.
- docs/MIGRATION-2.x-to-3.0.md - instruções para migrar instalações existentes.
- tests/test_dovecot_stats.sh - testes de regressão do coletor.
- tests/validate_templates.py - validador estático dos templates YAML.
- legacy/zabbix-5.0/ - template Zabbix 5.0 e scripts legados preservados.

## Dados monitorados

A versão 3.0.0 preserva os dados existentes:

- Disponibilidade do coletor e último erro.
- Conexões IMAP ativas.
- Conexões POP3 ativas.
- Total de conexões IMAP e POP3 ativas.
- Quantidade do processo master do Dovecot.
- Versão do Dovecot.
- Disponibilidade de IMAP, IMAPS, POP3 e POP3S.
- Tempo de resposta de IMAP, IMAPS, POP3 e POP3S.
- Alterações de checksum dos arquivos de configuração selecionados.

Também adiciona:

- Quantidade de usuários únicos com sessões IMAP/POP3 ativas.
- Maior quantidade de conexões IMAP/POP3 simultâneas de um único usuário.
- Versão do coletor.

O coletor nunca envia usernames ao Zabbix. Eles são usados apenas em memória para calcular contadores agregados.

## Arquitetura da coleta

A key master é:

~~~text
dovecot.stats
~~~

Exemplo:

~~~json
{"status":1,"imap":10,"pop3":2,"total":12,"users":8,"max_user_connections":3,"error":""}
~~~

Em caso de falha:

~~~json
{"status":0,"imap":0,"pop3":0,"total":0,"users":0,"max_user_connections":0,"error":"doveadm_who_failed"}
~~~

O coletor usa doveadm who -1, que retorna uma linha por usuário e conexão e evita subcontagem quando um usuário possui várias conexões simultâneas.

## Modelo de segurança

O coletor deve executar como usuário do Zabbix agent. Não conceda sudo ao script do coletor.

Primeiro ele tenta:

~~~text
doveadm who -1
~~~

sem elevar privilégios. Se o usuário zabbix não puder consultar o socket anvil, somente o mesmo comando é repetido com sudo -n.

FreeBSD:

~~~text
zabbix ALL=(root) NOPASSWD: /usr/local/bin/doveadm who -1
~~~

Linux:

~~~text
zabbix ALL=(root) NOPASSWD: /usr/bin/doveadm who -1
~~~

Não substitua essas regras por acesso irrestrito ao doveadm e não conceda NOPASSWD para dovecot_stats.sh.

Consulte SECURITY.md.

## Requisitos

- Zabbix 7.0 ou 8.0 conforme o export escolhido.
- Zabbix agent ou agent 2 no servidor Dovecot.
- Dovecot com doveadm disponível.
- POSIX shell e awk.
- sudo somente quando o usuário zabbix não conseguir consultar diretamente o socket anvil.

Caminhos comuns detectados automaticamente:

~~~text
FreeBSD
/usr/local/bin/doveadm
/usr/local/sbin/dovecot

Linux
/usr/bin/doveadm
/usr/sbin/dovecot
~~~

## Instalação

1. Instale o coletor:

~~~sh
install -o root -g wheel -m 0755 scripts/dovecot_stats.sh /usr/local/scripts/dovecot_stats.sh
~~~

No Linux, use o grupo de root apropriado para a distribuição.

2. Instale agent/userparameter_dovecot.conf no diretório de includes do Zabbix agent.

3. Teste primeiro o acesso direto:

~~~sh
sudo -u zabbix /usr/local/bin/doveadm who -1
~~~

ou no Linux:

~~~sh
sudo -u zabbix /usr/bin/doveadm who -1
~~~

4. Somente se o acesso direto falhar por permissão no socket, instale o exemplo de sudoers correspondente e valide com visudo -cf.

5. Reinicie o Zabbix agent.

6. Valide as keys:

~~~sh
sudo -u zabbix zabbix_agentd -t dovecot.stats
sudo -u zabbix zabbix_agentd -t dovecot.version
sudo -u zabbix zabbix_agentd -t dovecot.collector.version
~~~

7. Importe o YAML correspondente e vincule Template App Dovecot ao host.

## Verificações dos serviços

IMAP e POP3 sem TLS usam verificações de protocolo do Zabbix:

~~~text
net.tcp.service[imap,...]
net.tcp.service[pop,...]
~~~

IMAPS e POP3S permanecem verificações TCP porque os service checks do Zabbix agent não negociam IMAPS/POP3S nas portas 993/995.

## Checksum de configuração

Os itens de checksum da configuração principal e SQL foram preservados da versão 2.x.

Não reduza permissões de segurança de um arquivo apenas para permitir que o Zabbix calcule seu checksum. Se o agent não puder ler um arquivo protegido de forma segura, desabilite esse item no host ou use um mecanismo de integridade planejado para isso.

## Compatibilidade

| Componente | Status |
| --- | --- |
| Zabbix 7.0 | Export mantido |
| Zabbix 8.0 | Export mantido |
| Zabbix 6.0 | Planejado, ainda não validado |
| Dovecot 2.3 | Arquitetura do coletor compatível; validar no host |
| Dovecot 2.4 | Arquitetura do coletor compatível; validar no host |
| FreeBSD | Layout de caminhos suportado |
| Linux | Layout comum de caminhos suportado |

## Migração da versão 2.x

A versão 3.0.0 reorganiza o projeto nos diretórios scripts/ e agent/ e altera o modelo de sudo. As keys e UUIDs do template foram preservados sempre que viável para que a importação atualize os itens em vez de criar itens paralelos.

Leia docs/MIGRATION-2.x-to-3.0.md antes de atualizar um host existente.

## Validação

~~~sh
sh -n scripts/dovecot_stats.sh
sh tests/test_dovecot_stats.sh
python3 tests/validate_templates.py
~~~

O validador Python requer PyYAML apenas no ambiente de desenvolvimento/CI. O host monitorado não precisa de Python.

Veja docs/VALIDATION.md para a lista completa.

## Licença

Este projeto é distribuído sob a licença MIT. Consulte LICENSE.
