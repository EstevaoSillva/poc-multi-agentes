# Chat API DTO Moderno

## Objetivo

Este guia descreve como uma IA deve recriar o contrato de [`src/app/dto/chat-api.dto.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/dto/chat-api.dto.ts) com nomes de exemplo, tipagem forte e padrao moderno.

## Papel real do arquivo

Este DTO concentra os contratos de API do chat:

- papeis de mensagem
- historico enviado ao backend
- payload de envio de pergunta
- status de resposta
- contrato de visualizacao
- resumo de conversas
- contrato de mensagens por conversa
- erro tipado de integracao

## Como a IA deve recriar

Ao reimplementar esse arquivo, a IA deve preferir:

- `type` para unioes literais
- `interface` para payloads e respostas
- nomes neutros como `ConversationApiResponse`, `SendPromptPayload` e `ChartSpec`
- erro de dominio tipado com `extends Error` apenas quando realmente necessario

## Contrato que deve ser preservado

- existir tipo para role com `user`, `assistant` e `system`
- existir payload para envio de mensagem com texto, historico opcional, id de conversa opcional e arquivo opcional
- existir resposta de API com id da conversa, agente, status, conteudo e visualizacao opcional
- existir resumo de conversa para sidebar ou historico
- existir item de mensagem para tela de conversa
- existir erro tipado para camadas de UI e service

## Reimplementacao moderna sugerida

Use nomes neutros como:

- `ConversationRole`
- `ConversationHistoryItem`
- `SendPromptPayload`
- `ApiDeliveryStatus`
- `ChartSpec`
- `ConversationSummaryDto`
- `ConversationMessageDto`
- `ConversationApiError`

## Prompt recomendado para IA

```text
Recrie um arquivo DTO para API de chat com tipagem moderna em TypeScript.
Use type aliases para unions, interfaces para payloads e respostas, e nomes neutros.
Preserve contratos para envio de mensagem, historico, visualizacao, lista de conversas, mensagens de uma conversa e erro tipado.
Evite nomes reais do dominio.
```

## Erros comuns que a IA deve evitar

- usar `any` para visualizacao quando a estrutura pode ser parcialmente tipada
- misturar DTO de API com model de UI
- remover o erro tipado de dominio
- trocar `snake_case` de API sem deixar claro que houve mapeamento
