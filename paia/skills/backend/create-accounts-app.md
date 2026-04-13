**Descrição**: Você é especialista em criar a app `accounts` no padrão do PAIA, centralizando autenticação, usuário, perfil e fluxos de senha.

## Objetivo

Criar ou ajustar a app `accounts` como fronteira única para login, registro, `me`, perfis, papéis e mutações de senha.

## Fontes de verdade

- `docs/backend/accounts-instruct.md`
- `docs/backend/architeture-back.md`
- `specs/backend/backend-accounts-app.feature.md`
- `specs/backend/backend-auth-passwords.feature.md`

## Checklist

- A app `accounts` possui `models.py`, `serializers.py`, `viewsets.py`, `actions.py`, `messages.py`, `exceptions.py` e `urls.py`.
- A autenticação não ficou espalhada em `core` nem em apps de domínio.
- O projeto usa `AUTH_USER_MODEL` quando necessário.
- Relações de usuário em outras apps usam `settings.AUTH_USER_MODEL`.
- Os endpoints ficam sob `/api/accounts/`.
