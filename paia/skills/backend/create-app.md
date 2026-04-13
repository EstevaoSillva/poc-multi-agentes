**Descrição**: Você é especialista em criar uma app backend completa no padrão do PAIA.

## Objetivo

Criar uma app em `artifacts/backend/` com estrutura, rotas, configuração e contratos coerentes com a arquitetura do projeto, sempre sobre o skeleton `core` + `accounts`.

## Fontes de verdade

- `docs/backend/architeture-back.md`
- `specs/backend/backend-app-create.feature.md`
- `docs/backend/accounts-instruct.md` quando a app tratar autenticação ou usuário

## Entregáveis mínimos

- `models.py`
- `serializers.py`
- `viewsets.py`
- `actions.py`
- `messages.py`
- `exceptions.py`
- `urls.py`
- `tests/`

Arquivos opcionais conforme o caso:

- `behaviors.py`
- `filters.py`
- `managers.py`
- `tasks.py`

## Checklist

- A app foi criada no lugar correto.
- O skeleton `core` + `accounts` existe.
- A app foi incluída no `urls.py` principal.
- Não há credenciais nem configuração hardcoded.
- Se a app trata autenticação ou usuário, ela foi criada como `accounts`.
