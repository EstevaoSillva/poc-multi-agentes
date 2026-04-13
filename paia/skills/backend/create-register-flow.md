**Descrição**: Você é especialista em criar o fluxo de cadastro de usuário na app `accounts` no padrão do PAIA.

## Objetivo

Garantir cadastro consistente, seguro e transacional para criação de usuário, perfil, papel e demais dados de identidade.

## Fontes de verdade

- `docs/backend/accounts-instruct.md`
- `docs/backend/messages-instruct.md`
- `docs/backend/exceptions-instruct.md`
- `specs/features/register.feature.md`

## Checklist

- O cadastro usa serializer próprio.
- Username e email possuem validação de unicidade quando aplicável.
- A senha é persistida por `set_password(...)`.
- Perfil e papel são criados no fluxo correto quando aplicável.
- Mensagens e exceções foram centralizadas.
