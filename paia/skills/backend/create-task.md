**Descrição**: Você é especialista em criar `tasks.py` com Celery no padrão do PAIA.

## Objetivo

Implementar tarefas assíncronas com retry, fila explícita e delegação da regra principal para a camada certa.

## Fontes de verdade

- `docs/backend/tasks-instruct.md`
- `docs/backend/actions-instruct.md`
- `docs/backend/behaviors-instruct.md`

## Checklist

- A task usa `@shared_task`.
- A fila foi declarada explicitamente.
- `bind=True` foi usado quando necessário.
- A regra principal foi delegada.
- O disparo da task acontece após commit quando depende de persistência.
