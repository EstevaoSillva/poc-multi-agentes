# Advanced Filter DTO Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/dto/advanced-filter.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/dto/advanced-filter.ts) de forma moderna e tipada.

## Papel real do arquivo

O arquivo representa um agrupador nomeado de filtros avancados, com:

- nome da configuracao
- lista de filtros associados

## Como a IA deve recriar

Na versao moderna, a IA deve preferir:

- `interface` ou `type` em vez de `class` simples sem comportamento
- tipar os itens de `filters`
- usar nome neutro como `SavedFilterGroup`

## Contrato que deve ser preservado

- existir um nome da colecao de filtros
- existir um array de filtros
- a lista deve iniciar vazia quando apropriado

## Estrutura moderna sugerida

```ts
export interface SavedFilterGroup<TFilter = unknown> {
    name: string;
    filters: TFilter[];
}
```

## Prompt recomendado para IA

```text
Recrie um DTO simples que representa um grupo nomeado de filtros.
Prefira interface generica, tipagem forte e nomes neutros.
Evite classe vazia sem comportamento real.
```

## Erros comuns

- manter `filters: any[]`
- usar `class` quando o tipo e apenas estrutural
