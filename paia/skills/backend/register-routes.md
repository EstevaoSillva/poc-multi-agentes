**Descrição**: Você é especialista em registrar rotas de apps backend no padrão do PAIA.

## Objetivo

Criar ou ajustar `urls.py` da app e registrar a app no `urls.py` principal com coerência de prefixo e domínio.

## Fontes de verdade

- `docs/backend/urls-instruct.md`
- `specs/backend/backend-urls-routing.feature.md`

## Checklist

- A app possui `urls.py`.
- O `urls.py` principal inclui a app.
- O prefixo está sob `/api/`.
- O router e o `basename` estão coerentes com o domínio.
- Fluxos de autenticação e usuário usam `/api/accounts/` quando aplicável.
