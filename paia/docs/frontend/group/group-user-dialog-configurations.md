# group-user-dialog-configurations.ts

**Descrição**: Este documento orienta a IA a editar a configuração de filtros do diálogo de associação de usuários a grupos.

## Objetivo

Este guia orienta a IA a editar [`group-user-dialog-configurations.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/group/group-user/group-user-dialog/group-user-dialog-configurations.ts), usado pelos filtros do dialogo de associacao de usuarios.

## Responsabilidades reais

- Definir busca livre por `name`.
- Definir filtro de coluna por `name`.
- Manter a configuracao minima do dialogo consistente com `User`.

## Contrato que a IA deve preservar

- O arquivo deve continuar exportando `freeSearchTextConfiguration` e `columnsConfig`.
- Os campos definidos devem continuar compatíveis com a API de usuarios.
- O filtro principal deve continuar textual.

## Exemplo de edicao segura

Para alterar o label para o padrao de traducao do projeto:

```ts
export const freeSearchTextConfiguration: FilterConfiguration = {
    name: 'name',
    label: ['user', 'name'],
    fieldType: FieldType.STRING,
    filterType: FilterType.NORMAL,
};
```

Cuidados:

- Revise o componente consumidor para manter consistencia de UX.
- Nao mude o campo `name` para outro sem confirmar suporte no backend.

## Checklist para IA

- O nome do campo continua valido?
- Os labels estao consistentes com o restante do modulo?
- O tipo do filtro continua adequado para busca textual?

## Prompt recomendado para IA

```text
Edite group-user-dialog-configurations.ts mantendo compatibilidade com GroupUserDialogComponent.
- manter filtros coerentes com User
- usar labels traduziveis
- nao alterar o campo de busca sem confirmar suporte da API
```
