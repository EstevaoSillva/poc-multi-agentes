# Feature: Listagem de cursos

## Objetivo
Exibir os cursos cadastrados com suporte a busca, filtro e ação de inativação.

## Regras
- se não houver registros, deve ser exibida uma mensagem padrão de lista vazia
- a listagem deve permitir filtrar pelos campos principais do curso
- a ação de inativação não deve remover fisicamente o registro sem regra explícita
- mensagens de retorno e erros devem seguir `messages.py` e `exceptions.py`

## Tela
Formulário com:
- tabela com colunas de `id`, `nome`, `última atualização` e ação de inativação
- campos de filtro alinhados às colunas principais
- feedback de carregamento e de lista vazia

## Backend
Entidade esperada:
- `Course`

Arquivos esperados:
- `models.py`
- `serializers.py`
- `filters.py`
- `viewsets.py`
- `actions.py`
- `messages.py`
- `exceptions.py`
- `urls.py`

Endpoints:
- `GET /api/courses/`
- `PATCH /api/courses/<id>/`

Comportamentos esperados:
- listagem com `filterset_class`
- ordenação por campos relevantes
- inativação via action ou update controlado por `actions.py`
- mensagens reutilizáveis centralizadas
- exceções de domínio para curso inexistente ou operação inválida

## Checklist
- a listagem usa filtros consistentes com `filters.py`?
- a inativação passa por `actions.py`?
- a resposta evita N+1?
- a regra de exclusão lógica está clara?
- existem mensagens de lista vazia, sucesso e erro?
