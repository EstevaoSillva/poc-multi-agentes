# Module Model Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/models/account/module.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/models/account/module.ts) em formato moderno.

## Papel real do arquivo

Esse model representa um modulo, workspace ou area funcional da aplicacao com:

- `id`
- `url`
- `description`
- `icon`
- `granted`

## Contrato que deve ser preservado

- existir identificador
- existir url
- existir descricao
- existir icone
- existir flag de permissao

## Reimplementacao moderna sugerida

```ts
export interface WorkspaceModule {
    id: number;
    url: string;
    description: string;
    icon: string;
    granted: boolean;
}
```

## Prompt recomendado para IA

```text
Recrie um model de modulo ou workspace com id, url, descricao, icone e granted.
Use interface e nomes neutros.
```

## Erros comuns

- misturar modulo com menu
- remover o campo de permissao
