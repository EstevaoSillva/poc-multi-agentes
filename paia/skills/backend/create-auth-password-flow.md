**Descrição**: Você é especialista em criar fluxos de login, registro, refresh token, troca de senha e reset de senha no padrão do PAIA.

## Objetivo

Garantir contratos estáveis e seguros para autenticação e senha dentro da app `accounts`.

## Fontes de verdade

- `docs/backend/accounts-instruct.md`
- `docs/backend/messages-instruct.md`
- `docs/backend/exceptions-instruct.md`
- `specs/backend/backend-auth-passwords.feature.md`
- `specs/features/login.feature.md`
- `specs/features/register.feature.md`
- `specs/features/password-recovery.feature.md`

## Checklist

- Login e refresh têm serializers próprios.
- `SIMPLE_JWT` está configurado com timeout explícito.
- `JWT_ACCESS_TOKEN_MINUTES` e `JWT_REFRESH_TOKEN_DAYS` foram considerados.
- Registro usa fluxo seguro de criação de usuário.
- Mudança de senha valida senha atual quando aplicável.
- Reset de senha usa token e validade.
- Recuperação de senha não vaza existência do usuário.
- Mensagens e exceções foram centralizadas.
