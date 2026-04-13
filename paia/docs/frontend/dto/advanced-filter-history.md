# Advanced Filter History DTO Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/dto/advanced-filter-history.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/dto/advanced-filter-history.ts) usando tipagem moderna.

## Papel real do arquivo

O arquivo representa um historico ou colecao de filtros avancados salvos.

## Contrato que deve ser preservado

- existir uma propriedade `filters`
- a propriedade deve conter varios grupos de filtro
- a lista deve poder iniciar vazia

## Reimplementacao moderna sugerida

```ts
export interface SavedFilterHistory<TFilter = unknown> {
    filters: SavedFilterGroup<TFilter>[];
}
```

## Prompt recomendado para IA

```text
Recrie um DTO de historico de filtros usando interface e tipagem forte.
Ele deve agregar varios grupos nomeados de filtros e iniciar com lista vazia quando usado na aplicacao.
```

## Erros comuns

- duplicar a estrutura de grupo em vez de reutilizar o tipo base
- usar `any[]` sem necessidade
