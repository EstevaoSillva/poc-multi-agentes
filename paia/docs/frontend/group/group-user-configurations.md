# group-user-configurations.ts

**Descrição**: Este documento orienta a IA a editar a configuração de filtros da listagem de usuários associados a um grupo.

## Objetivo

Este guia orienta a IA a editar [`group-user-configurations.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/group/group-user/group-user-configurations.ts), que define os filtros usados na listagem de usuarios associados ao grupo.

## Responsabilidades reais

- Configurar busca livre pelo campo `name`.
- Configurar filtro de coluna para `name`.
- Manter labels alinhadas com a traducao de usuarios.

## Contrato que a IA deve preservar

- O nome do campo continua sendo `name`.
- O `fieldType` continua `STRING`.
- O arquivo continua exportando `freeSearchTextConfiguration` e `columnsConfig`.

## Exemplo de edicao segura

Para adicionar busca por email:

```ts
{
    name: 'email',
    label: 'email',
    fieldType: FieldType.STRING,
    filterType: FilterType.NORMAL,
}
```

Cuidados:

- So adicione esse campo se a API realmente filtrar por `email`.
- Revise o template e a tabela se quiser exibir a nova coluna.

## Checklist para IA

- Os campos configurados existem em `User` e na API?
- Os labels seguem o padrao de i18n?
- A busca livre continua priorizando o campo principal correto?

## Prompt recomendado para IA

```text
Edite group-user-configurations.ts preservando a compatibilidade com GroupUserComponent.
- manter nomes de campos validos para a API
- manter filtros simples e coerentes com User
- ajustar labels para traducao quando necessario
```
