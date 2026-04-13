# Choice DTO Moderno

## Objetivo

Este guia descreve como a IA deve recriar [`src/app/dto/choice.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/dto/choice.ts) com tipagem forte e nomes neutros.

## Papel real do arquivo

O tipo representa uma opcao para selects, filtros ou choices vindos de `OPTIONS`:

- valor interno
- texto exibido

## Como a IA deve recriar

Na versao moderna, preferir um tipo generico:

```ts
export interface SelectOption<TValue = string> {
    value: TValue;
    label: string;
}
```

## Contrato que deve ser preservado

- existir um valor serializavel ou identificador
- existir um texto de exibicao

## Prompt recomendado para IA

```text
Recrie um DTO de opcao para selects usando interface generica e nomes neutros.
Preserve os papeis de value e texto exibido.
Evite display_name e any sem motivo.
```

## Erros comuns

- usar `display_name` em modelo interno sem necessidade
- deixar `value` como `any`
