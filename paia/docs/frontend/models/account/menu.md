# Menu Model Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/models/account/menu.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/models/account/menu.ts) em forma moderna.

## Papel real do arquivo

O model representa um item de menu navegavel com:

- identificador
- url
- descricao
- icone
- flag extra de associacao

## Contrato que deve ser preservado

- existir `id`
- existir `url`
- existir texto descritivo
- existir icone
- existir flag booleana de associacao

## Reimplementacao moderna sugerida

```ts
export interface NavigationItem {
    id: number;
    url: string;
    label: string;
    icon: string;
    associated: boolean;
}
```

## Prompt recomendado para IA

```text
Recrie um model de item de navegacao com id, url, label, icon e estado de associacao.
Use interface e nomes neutros.
```

## Erros comuns

- misturar menu com permissao de menu
- remover a flag de associacao
