**Descrição**: Você é especialista em criar o service de sessão do frontend para login, tokens, refresh, logout e usuário autenticado.

## Objetivo

Garantir uma camada de sessão centralizada, moderna e coerente com o backend `accounts`.

## Fontes de verdade

- `docs/frontend/accounts/auth.service.md`
- `docs/frontend/architeture-front.md`
- `specs/frontend/frontend-auth-session.feature.md`

## Checklist

- Existe método de login.
- Existe método de refresh token.
- Tokens são persistidos e limpos corretamente.
- O usuário autenticado fica disponível para consumo.
- O service permanece centralizado em `accounts`.
