# Chat Model Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/models/chat.model.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/models/chat.model.ts) usando modelagem moderna e nomes neutros.

## Papel real do arquivo

O model representa um registro de interacao de chat persistida, com:

- identificador interno
- identificador externo da conversa
- pergunta
- resposta
- agente
- status
- fonte
- indicativo de fallback
- dados visuais opcionais
- data de criacao

## Contrato que deve ser preservado

- existir id numerico
- existir id logico da conversa
- existir texto de pergunta e resposta
- existir agente e status
- existir payload visual opcional
- existir informacao se houve fallback

## Reimplementacao moderna sugerida

```ts
export interface ConversationRecord extends EntityBase {
    conversationId: string;
    prompt: string;
    reply: string;
    agentName: string;
    status: string;
    source?: string | null;
    fallbackUsed: boolean;
    visualizationData?: Record<string, unknown> | null;
}
```

## Prompt recomendado para IA

```text
Recrie um model de registro de chat persistido usando interface e nomes neutros.
Preserve conversa, pergunta, resposta, agente, status, fallback e visualizacao opcional.
```

## Erros comuns

- misturar esse model com DTO de API
- perder o campo de fallback
