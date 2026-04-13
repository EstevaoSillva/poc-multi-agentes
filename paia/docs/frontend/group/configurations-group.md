# configurations-group.ts

**Descrição**: Este documento orienta a IA a editar a configuração de filtros da tela de grupos, mantendo compatibilidade com a API e com os componentes consumidores.

## Objetivo

Este arquivo orienta a IA a editar [`configurations-group.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/group/configurations-group.ts), que centraliza as configuracoes de filtro da tela de grupos.

## Responsabilidades reais

- Definir o filtro de busca livre por `name`.
- Definir filtros por coluna para `id` e `name`.
- Manter consistencia entre filtros, labels traduziveis e tipos de campo.

## Contrato que a IA deve preservar

- `freeSearchTextConfiguration.name` deve continuar compatível com a API.
- `columnsConfig` deve refletir campos reais retornados pela listagem.
- `fieldType` e `filterType` devem continuar coerentes com cada campo.

## Exemplo de criacao de configuracao

```ts
export const freeSearchTextConfiguration: FilterConfiguration = {
    name: 'description',
    label: 'department',
    fieldType: FieldType.STRING,
    filterType: FilterType.NORMAL,
};

export const columnsConfig: FilterConfiguration[] = [
    {
        name: 'id',
        label: 'code',
        fieldType: FieldType.NUMBER,
        filterType: FilterType.NORMAL,
    },
    {
        name: 'description',
        label: 'department',
        fieldType: FieldType.STRING,
        filterType: FilterType.NORMAL,
    },
];
```

## Exemplo de edicao segura

Para adicionar filtro por status:

```ts
{
    name: 'is_active',
    label: 'status',
    fieldType: FieldType.BOOLEAN,
    filterType: FilterType.NORMAL,
}
```

Cuidados:

- So adicionar o filtro se a API aceitar esse parametro.
- Revisar o componente que consome `columnsConfig`.
- Garantir label compatível com traducao do projeto.

## Checklist para IA

- Os nomes dos campos existem na API?
- O tipo do filtro corresponde ao tipo do campo?
- O label segue o padrao de i18n do projeto?
- A busca livre foi mantida em um campo textual adequado?

## Prompt recomendado para IA

```text
Edite configurations-group.ts preservando a compatibilidade com o componente GroupComponent e com a API.
- manter FilterConfiguration consistente
- usar nomes de campos reais da resposta backend
- ajustar labels para traducao
- nao adicionar filtros que a API nao entende
```
