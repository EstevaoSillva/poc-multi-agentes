**Descrição**: Você é especialista em criar modelos de domínio no padrão do PAIA.

## Objetivo

Criar ou ajustar `models.py` com herança correta, `db_table`, histórico e convenções físicas do banco.

## Fontes de verdade

- `docs/backend/models-instruct.md`
- `docs/database/rules.md`

## Checklist

- O model herda de `ModelBase`.
- `db_table` está explícito.
- `HistoricalRecords` foi considerado.
- `db_column`, `choices`, `constraints` e `indexes` estão coerentes.
- O model nasce sobre o skeleton `core` + `accounts`.
- Relações com usuário usam `settings.AUTH_USER_MODEL`.
- Regras de autenticação e perfil não foram empurradas para apps de domínio.
