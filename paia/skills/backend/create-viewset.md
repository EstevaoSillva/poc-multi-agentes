**Descrição**: Você é especialista em criar `viewsets.py` no padrão do PAIA.

## Objetivo

Criar endpoints DRF organizados por domínio, usando a base compartilhada e delegando regra de negócio para as camadas corretas.

## Fontes de verdade

- `docs/backend/viewsets-instruct.md`
- `docs/backend/urls-instruct.md`
- `docs/backend/actions-instruct.md`

## Checklist

- O viewset herda da base correta.
- Existe `queryset`, `serializer_class`, `ordering`.
- Existe `filterset_class` quando necessário.
- Regra complexa não ficou no viewset.
- A rota da app foi registrada.
