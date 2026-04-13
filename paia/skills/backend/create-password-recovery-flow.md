**Descrição**: Você é especialista em criar o fluxo de recuperação e redefinição de senha na app `accounts` no padrão do PAIA.

## Objetivo

Garantir solicitação de recuperação, emissão de token, redefinição de senha e mensagens seguras sem vazamento de identidade.

## Fontes de verdade

- `docs/backend/accounts-instruct.md`
- `docs/backend/messages-instruct.md`
- `docs/backend/exceptions-instruct.md`
- `specs/features/password-recovery.feature.md`

## Checklist

- Existem serializers separados para solicitação e redefinição.
- A solicitação não revela se o usuário existe.
- O token possui validade explícita.
- A redefinição valida token, senha e confirmação.
- Envio de notificação fica desacoplado quando houver tarefa assíncrona.
