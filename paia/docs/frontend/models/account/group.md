# Group Model Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/models/account/group.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/models/account/group.ts) usando nomes neutros.

## Papel real do arquivo

O model representa um agrupamento de permissao ou acesso com:

- `id`
- `url`
- `name`
- `granted`

## Contrato que deve ser preservado

- existir identificador
- existir url do recurso
- existir nome do grupo
- existir flag de concessao

## Reimplementacao moderna sugerida

```ts
export interface AccessGroup {
    id: number;
    url: string;
    name: string;
    granted: boolean;
}
```

## Prompt recomendado para IA

```text
Recrie um model simples de grupo de acesso com id, url, nome e granted.
Use interface e nomes neutros.
```

## Erros comuns

- confundir grupo com usuario ou modulo
- remover `granted`
