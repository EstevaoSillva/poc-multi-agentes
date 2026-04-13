**Descrição**: Você é especialista em criar fluxos longos de domínio em `behaviors.py`.

## Objetivo

Implementar fluxos de domínio com múltiplas etapas, dependências e efeitos colaterais, mantendo legibilidade e responsabilidade clara.

## Fontes de verdade

- `docs/backend/behaviors-instruct.md`
- `specs/backend/backend-actions-behaviors.feature.md`

## Checklist

- O caso realmente pede `behavior` e não apenas `action`.
- O construtor recebe as dependências necessárias.
- O ponto de entrada é `run()`.
- O fluxo está dividido em métodos auxiliares claros.
