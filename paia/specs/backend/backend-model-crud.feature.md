# Feature: CRUD base de entidade backend

## Objetivo
Definir o contrato mínimo para criar uma entidade de domínio completa no backend com model, serializer, filtros, viewset, action, mensagens, exceções, rota e testes.

## Escopo
- entidade CRUD padrão
- listagem com filtro e ordenação
- criação, detalhe, atualização parcial e exclusão
- mensagens e exceções consistentes

## Regras
- o model deve herdar de `core_models.ModelBase`
- deve existir `Meta.db_table` com schema explícito
- o model deve usar `HistoricalRecords` quando seguir o padrão do domínio
- operações de escrita devem passar por `actions.py`
- viewset deve herdar da base de `core/viewsets.py`
- serializer deve herdar da base de `core/serializers.py`
- quando houver expansão de campos, o serializer deve usar `rest_flex_fields`
- filtro deve usar `django-filter`
- erros de domínio devem usar `exceptions.py`
- mensagens reutilizáveis devem ficar em `messages.py`
- autenticação e mutações de senha não devem nascer em CRUDs de apps de domínio

## Entregáveis
- model de domínio
- manager e queryset quando a leitura exigir reuso
- filterset
- serializer
- action de create
- action de update
- action de delete
- viewset
- `urls.py` da app
- mensagens e exceções da feature
- testes unitários e de API

## Contrato da API
- `GET /api/<app>/<entities>/`
- `POST /api/<app>/<entities>/`
- `GET /api/<app>/<entities>/<id>/`
- `PATCH /api/<app>/<entities>/<id>/`
- `DELETE /api/<app>/<entities>/<id>/`

## Padrões esperados
- `select_related` e `prefetch_related` para evitar N+1
- `@transaction.atomic` nas ações de escrita
- `filterset_class` no viewset
- `ordering` e `ordering_fields`
- não registrar `drf_flex_fields` em `INSTALLED_APPS`
- `db_column`, `choices`, `constraints`, `indexes` e `related_name` coerentes
- relacionamentos com usuário devem usar `settings.AUTH_USER_MODEL` quando aplicável
- mensagens reaproveitáveis centralizadas
- exceções de domínio com `APIException`

## Referências
- `docs/backend/models-instruct.md`
- `docs/backend/serializers-instruct.md`
- `docs/backend/viewsets-instruct.md`
- `docs/backend/actions-instruct.md`
- `docs/backend/filters-instruct.md`
- `docs/backend/managers-instruct.md`
- `docs/backend/messages-instruct.md`
- `docs/backend/exceptions-instruct.md`

## Checklist
- o model usa a base correta?
- a listagem possui filtro e ordenação?
- o serializer não concentra regra de negócio indevida?
- o viewset delega escrita para `actions.py`?
- existem mensagens e exceções consistentes para o domínio?
- há testes de fluxo feliz, validação e erro de negócio?
