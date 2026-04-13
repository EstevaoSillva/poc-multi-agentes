# GroupUserComponent

**Descrição**: Este documento orienta a IA a criar e editar o `GroupUserComponent`, responsável por listar usuários associados a um grupo e abrir o diálogo de associação.

## Objetivo

Este guia orienta a IA a criar e editar [`GroupUserComponent`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/group/group-user/group-user.component.ts), que lista os usuarios associados a um grupo e abre o dialogo para novas associacoes.

## Responsabilidades reais

- Receber um `Group` via `input<Group>()`.
- Listar usuarios associados usando endpoint `URLS.USER`.
- Consultar a rota `find_group_associated`.
- Informar `target` com o `id` do grupo antes da busca.
- Usar `associate_group` como rota de associacao.
- Abrir `GroupUserDialogComponent` para associar novos usuarios.

## Contrato que a IA deve preservar

- `group()` deve continuar sendo a fonte do `target`.
- `search()` deve limpar parametros e reenviar `target`.
- `displayedColumns` deve permanecer consistente com o template.
- O dialogo deve continuar recebendo o grupo atual em `data`.
- Ao fechar o dialogo, a lista deve ser recarregada com `search(true)`.

## Exemplo de criacao de componente parecido

```ts
export class TeamMemberComponent extends BaseComponentListDirective<User> {
    public team = input<Team>();
    public displayedColumns = ['id', 'user', 'action'];

    constructor(public injector: Injector) {
        super(injector, {
            pk: 'id',
            endpoint: URLS.USER,
            associativeRoute: 'associate_team',
            searchRoute: 'find_team_associated',
            paramsOnInit: { ordering: 'name', associated: true },
            searchOnInit: true,
        });
    }

    public override search(restartIndex?: boolean): void {
        this.service.clearParameter();
        this.service.addParameter('target', this.team().id);
        super.search(restartIndex);
    }
}
```

## Exemplo de edicao segura

Para ordenar por email em vez de nome:

```ts
const BASE_OPTIONS: BaseListComponentOptions = {
    pk: 'id',
    endpoint: URLS.USER,
    associativeRoute: 'associate_group',
    searchRoute: 'find_group_associated',
    paramsOnInit: { ordering: 'email', associated: true },
    searchOnInit: true,
};
```

Cuidados:

- Garantir que a API aceita esse `ordering`.
- Ajustar filtros se a busca livre deixar de fazer sentido.
- Nao remover o parametro `target`.

## Checklist para IA

- `group()` pode estar indefinido em algum ciclo de vida?
- O target do grupo esta sendo enviado em toda busca?
- O dialogo de associacao ainda reabre a busca ao fechar?
- A rota `associate_group` continua correta?
- Os filtros importados ainda combinam com `User`?

## Prompt recomendado para IA

```text
Edite o GroupUserComponent preservando o fluxo de associacao de usuarios a grupos.
- manter heranca de BaseComponentListDirective<User>
- manter searchRoute find_group_associated e associativeRoute associate_group
- manter target baseado em group().id
- manter dialogo GroupUserDialogComponent com refresh apos close
- reaproveitar filtros de group-user-configurations.ts
```
