# GroupComponent

**Descrição**: Este documento orienta a IA a criar, editar e manter o `GroupComponent`, tela principal de listagem de grupos.

## Objetivo

Este guia descreve como uma IA deve criar, editar e manter [`GroupComponent`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/group/group.component.ts), que representa a tela principal de listagem de grupos.

O componente herda de `BaseComponentListDirective<Group>` e funciona como entrada do CRUD de grupos.

## Responsabilidades reais

- Listar grupos a partir de `URLS.GROUP`.
- Iniciar busca automaticamente com `searchOnInit: true`.
- Expor filtros livres e por coluna usando `configurations-group.ts`.
- Definir as colunas principais da tabela: `name` e `actions`.
- Reaproveitar `formRoute: WEB.GROUP` para navegacao.

## Contrato que a IA deve preservar

- O `BASE_OPTIONS` deve continuar apontando para `URLS.GROUP`.
- `formTitle` deve continuar associado a `group-management`.
- `displayedColumns` deve manter coerencia com o template real.
- O tipo de `object` deve continuar sendo `Group`.
- Os filtros devem continuar vindos de `columnsConfig` e `freeSearchTextConfiguration`.

## Exemplo de criacao de listagem parecida

```ts
export class DepartmentComponent extends BaseComponentListDirective<Department> {
    public displayedColumns = ['name', 'actions'];
    public object: Department = new Department();

    protected readonly columnsConfig = columnsConfig;
    protected readonly freeSearchTextConfiguration = freeSearchTextConfiguration;

    constructor(public injector: Injector) {
        super(injector, {
            formTitle: 'department-management',
            searchOnInit: true,
            endpoint: URLS.DEPARTMENT,
            formRoute: WEB.DEPARTMENT,
        });
    }
}
```

## Exemplo de edicao segura

Se a IA precisar adicionar a coluna `id` na tabela:

```ts
public displayedColumns: string[] = ['id', 'name', 'actions'];
```

Regras:

- Ajustar tambem o template da tabela.
- Nao mudar nomes de colunas sem revisar filtros, ordenacao e traducao.
- Nao mover a logica de busca para o componente se a base ja resolve.

## Checklist para IA

- A listagem ainda usa `BaseComponentListDirective<Group>`?
- O endpoint continua sendo o de grupos?
- As colunas declaradas existem no HTML?
- Os filtros importados ainda correspondem aos campos da API?
- `searchOnInit` continua adequado para a UX da tela?

## Prompt recomendado para IA

```text
Edite o GroupComponent preservando o padrao de listagem do projeto.
- manter heranca de BaseComponentListDirective<Group>
- manter endpoint URLS.GROUP e formRoute WEB.GROUP
- reaproveitar columnsConfig e freeSearchTextConfiguration
- alterar displayedColumns somente se o template acompanhar
- nao duplicar logica de busca, delete ou navegacao fora da base
```

## Erros comuns

- Trocar o endpoint por rota de detalhe.
- Adicionar filtros sem atualizar o arquivo de configuracao.
- Mudar `displayedColumns` sem alterar o template.
- Substituir a base por chamadas diretas ao servico.
