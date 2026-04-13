# Chat DTO Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/dto/chat.dto.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/dto/chat.dto.ts) usando contratos claros e separados para conversa e mensagem.

## Papel real do arquivo

O arquivo define dois DTOs simples:

- resumo de conversa
- mensagem de conversa

## Contrato que deve ser preservado

- existir entidade de conversa com `id`, `title`, `created_at` e `updated_at`
- existir entidade de mensagem com `id`, `role`, `content` e `created_at`
- o role da mensagem deve continuar restrito a papeis conhecidos

## Reimplementacao moderna sugerida

```ts
export type ConversationRole = 'user' | 'assistant' | 'system';

export interface ConversationDto {
    id: number;
    title: string;
    createdAt: string;
    updatedAt: string;
}

export interface ConversationMessageDto {
    id: number;
    role: ConversationRole;
    content: string;
    createdAt: string;
}
```

## Prompt recomendado para IA

```text
Recrie DTOs simples para conversa e mensagem de chat.
Use interfaces, role tipado e nomes neutros.
Se converter snake_case para camelCase, deixe isso explicito na camada de mapper.
```

## Erros comuns

- misturar esse DTO com o contrato completo da API de chat
- usar `string` livre para role
