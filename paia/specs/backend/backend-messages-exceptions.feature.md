# Feature: Mensagens e exceções de domínio

## Objetivo
Padronizar a criação de mensagens reutilizáveis e exceções de domínio para novas apps e novas features do backend.

## Regras
- mensagens compartilhadas devem ficar em `messages.py`
- exceções de domínio devem herdar de `APIException`
- exceções devem reutilizar constantes de `messages.py` sempre que possível
- `ValidationError` deve ficar restrito a erro de contrato ou payload
- strings duplicadas entre action, serializer, task e exception devem ser evitadas

## Entregáveis
- `messages.py` com constantes traduzíveis
- `exceptions.py` com exceções semânticas do domínio
- reutilização dessas mensagens em actions, serializers, tasks e viewsets

## Padrões esperados
- constantes em caixa alta com `_`
- mensagens com `gettext_lazy as _`
- exceptions com `status_code`
- exceptions com `default_detail`
- nome de exception semântico e terminado em `Exception`

## Exemplos de casos
- recurso não encontrado
- regra de negócio inválida
- operação bloqueada por dependências
- mensagem operacional de processamento assíncrono

## Referências
- `docs/backend/messages-instruct.md`
- `docs/backend/exceptions-instruct.md`

## Checklist
- a mensagem precisava mesmo ser centralizada?
- a exceção usa `messages.py`?
- a escolha entre `APIException` e `ValidationError` está correta?
- não há texto literal duplicado em múltiplos pontos?
