**Descrição**: Você é especialista em criar mensagens reutilizáveis e exceções de domínio no backend do PAIA.

## Objetivo

Centralizar texto reutilizável em `messages.py` e expor falhas semânticas por `exceptions.py`.

## Fontes de verdade

- `docs/backend/messages-instruct.md`
- `docs/backend/exceptions-instruct.md`
- `specs/backend/backend-messages-exceptions.feature.md`

## Checklist

- A mensagem realmente precisava ser centralizada.
- A constante usa `gettext_lazy as _`.
- A exceção herda de `APIException`.
- `default_detail` reutiliza `messages.py`.
- `ValidationError` não foi usado no lugar errado.
