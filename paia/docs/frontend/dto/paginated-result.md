# Paginated Result DTO Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/dto/paginated-result.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/dto/paginated-result.ts) de forma generica e tipada.

## Papel real do arquivo

O tipo representa uma resposta paginada de API com:

- quantidade total
- links ou cursores de pagina anterior e seguinte
- resultados
- header adicional opcional

## Como a IA deve recriar

Na versao moderna, a IA deve preferir `interface` generica:

```ts
export interface PagedResponse<TItem> {
    count: number;
    next: string | null;
    previous: string | null;
    results: TItem[];
    header?: unknown;
}
```

## Contrato que deve ser preservado

- existir `count`
- existir `next`
- existir `previous`
- existir `results`
- permitir metadado complementar opcional

## Prompt recomendado para IA

```text
Recrie um DTO generico para respostas paginadas de API.
Use interface, nomes neutros e tipos corretos para next e previous.
Evite classe com defaults quando o tipo e apenas estrutural.
```

## Erros comuns

- usar string vazia em vez de `null` sem necessidade
- misturar paginação com metadados específicos de UI
