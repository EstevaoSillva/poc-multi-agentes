# Model Base Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/models/model-base.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/models/model-base.ts) de forma moderna e reutilizavel.

## Papel real do arquivo

O arquivo define um conjunto minimo de campos comuns para varias entidades:

- `id`
- datas de criacao e alteracao
- flag de ativo

## Como a IA deve recriar

Na versao moderna, a IA deve preferir um tipo base estrutural:

```ts
export interface EntityBase {
    id?: number;
    createdAt?: string;
    updatedAt?: string;
    active?: boolean;
}
```

## Contrato que deve ser preservado

- existir identificador opcional
- existir timestamps opcionais
- existir flag booleana opcional de estado

## Prompt recomendado para IA

```text
Recrie um tipo base compartilhado para entidades.
Use interface e nomes neutros.
Mantenha apenas os campos realmente comuns.
```

## Erros comuns

- colocar regras de dominio nesse tipo base
- forcar toda entidade a herdar de classe se so precisa de shape
