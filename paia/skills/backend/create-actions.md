**Descrição**: Você é especialista em criar e ajustar `actions.py` no backend Django/DRF do PAIA.

## Objetivo

Implementar mutações síncronas e reutilizáveis de domínio em `actions.py`, mantendo transação, clareza, reuso e consistência com a arquitetura do projeto.

## Fontes de verdade

- `docs/backend/actions-instruct.md`
- `docs/backend/architeture-back.md`
- `docs/backend/messages-instruct.md`
- `docs/backend/exceptions-instruct.md`
- `docs/backend/tasks-instruct.md`

## Regras obrigatórias

1. Toda mutação relevante deve preferir `@transaction.atomic`.
2. `actions.py` é a fronteira oficial da regra de negócio síncrona.
3. A action deve receber dados já validados sempre que possível.
4. Campos auxiliares como `files`, `images` e listas transitórias não devem ser persistidos diretamente.
5. Use `transaction.on_commit(...)` para tasks, eventos ou integrações externas.
6. Regras de negócio inválidas devem usar exceções explícitas.
7. Mensagens reutilizáveis devem vir de `messages.py`.

## Fluxo de implementação

1. Identifique a entidade principal e o verbo da ação.
2. Defina se o caso é CRUD simples ou ação de domínio.
3. Filtre payload persistível.
4. Valide pré-condições.
5. Otimize consultas com `select_related` e `prefetch_related` quando necessário.
6. Persista dentro de transação.
7. Agende efeitos externos após commit.

## Checklist

- A regra ficou em `actions.py` e não em serializer ou viewset.
- Existe transação quando há mutação.
- Existe exceção semântica quando a regra falha.
- Mensagens compartilhadas não estão inline sem necessidade.
- Processamento assíncrono não foi disparado antes do commit.
