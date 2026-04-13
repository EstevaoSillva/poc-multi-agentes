# Module Menu Model Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/models/account/module-menu.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/models/account/module-menu.ts) com nomes de exemplo e tipagem forte.

## Papel real do arquivo

Esse model representa o vinculo entre:

- um modulo
- um menu
- um menu raiz opcional
- ordem de exibicao
- estado ativo
- permissao concedida

## Contrato que deve ser preservado

- existir `id`
- existir `url`
- existir referencia para item raiz
- existir referencia para modulo
- existir referencia para menu
- existir ordem
- existir flag de divisor
- existir flags de ativo e permissao

## Reimplementacao moderna sugerida

```ts
export interface WorkspaceMenuLink {
    id: number;
    url: string;
    root: string | NavigationItem;
    workspace: string | WorkspaceModule;
    item: string | number | NavigationItem;
    hasDivider: boolean;
    order: number;
    active: boolean;
    granted: boolean;
}
```

## Prompt recomendado para IA

```text
Recrie um model que representa o vinculo entre modulo e menu, com ordem, ativo, divisor e permissao.
Use nomes neutros e interfaces.
```

## Erros comuns

- perder a possibilidade de o relacionamento vir expandido ou por id
- remover `granted`
