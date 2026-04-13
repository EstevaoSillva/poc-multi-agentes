# Feature: Criação de app backend Django

## Objetivo
Criar uma nova app backend no padrão do PAIA, pronta para crescer por domínio sem desalinhar arquitetura, configuração, rotas, mensagens, exceções e regras de negócio.

## Escopo
- criar a app dentro de `artifacts/backend/`
- alinhar o skeleton base em `core` e `accounts`
- estruturar arquivos principais da app
- registrar rotas da app no projeto
- preparar a app para testes e evolução futura

## Regras
- a app deve respeitar [architeture-back.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/architeture-back.md)
- models devem seguir [models-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/models-instruct.md)
- serializers devem seguir [serializers-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/serializers-instruct.md)
- viewsets devem seguir [viewsets-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/viewsets-instruct.md)
- regras síncronas devem preferir [actions-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/actions-instruct.md)
- fluxos longos devem preferir [behaviors-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/behaviors-instruct.md)
- jobs assíncronos devem seguir [tasks-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/tasks-instruct.md)
- filtros devem seguir [filters-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/filters-instruct.md)
- managers devem seguir [managers-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/managers-instruct.md)
- mensagens e exceções devem seguir [messages-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/messages-instruct.md) e [exceptions-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/exceptions-instruct.md)
- configuração deve seguir [conf-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/conf-instruct.md)
- a app nova deve considerar `core` e `accounts` como skeleton padrão do projeto

## Estrutura esperada
App com:
- `models.py`
- `serializers.py`
- `viewsets.py`
- `actions.py`
- `behaviors.py` quando necessário
- `filters.py` quando houver listagem filtrável
- `managers.py` quando houver consulta reutilizável
- `messages.py`
- `exceptions.py`
- `tasks.py` quando houver assíncrono
- `urls.py`
- `tests/`

## Contrato técnico mínimo
- base compartilhada em `core/models.py`, `core/serializers.py` e `core/viewsets.py` deve existir quando o domínio depender dela
- autenticação, identidade e contexto do usuário devem ser consumidos de `accounts`
- se usar `drf-flex-fields`, o import deve ser `rest_flex_fields` e a biblioteca não deve entrar em `INSTALLED_APPS`
- se a app criada tratar autenticação ou usuário, ela deve ser `accounts`
- a app não deve hardcode credenciais nem parâmetros de conexão
- o banco deve ser PostgreSQL com `DB_*`
- storage deve usar `AWS_*` quando houver arquivos
- rotas devem ficar sob `/api/<app>/`

## Entregáveis
- app criada no local correto
- skeleton `core` + `accounts` alinhado
- app registrada no projeto
- rota principal incluída no `urls.py`
- estrutura mínima pronta para CRUD
- base documental e testes mínimos preparados

## Checklist
- a app foi criada dentro de `artifacts/backend/`?
- o skeleton `core` + `accounts` existe ou foi alinhado?
- a app tem `messages.py` e `exceptions.py`?
- a lógica de negócio ficou fora de serializer e viewset?
- o `urls.py` principal inclui a app?
- a app está preparada para testes e evolução sem retrabalho estrutural?
