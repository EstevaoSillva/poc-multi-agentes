# MenuPermissionComponent

**Descrição**: Este documento orienta a IA a criar e editar o `MenuPermissionComponent`, responsável por listar menus e alternar permissões de acesso para um grupo.

## Objetivo

Este guia documenta como a IA deve criar e editar [`MenuPermissionComponent`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/group/menu-permission/menu-permission.component.ts), responsavel por listar menus e alternar permissoes de acesso para um grupo.

## Responsabilidades reais

- Listar `ModuleMenu` usando endpoint `URLS.MODULE_MENU`.
- Consultar a rota `with_granted`.
- Incluir parametros fixos de ordenacao, expansao e filtros de menus ativos.
- Receber o grupo via `input.required<Group>()`.
- Carregar o usuario logado antes da busca.
- Conceder ou remover acesso por `postFromDetailRoute(..., 'grant', payload)`.

## Contrato que a IA deve preservar

- `group` deve continuar sendo um `InputSignal<Group>`.
- `loggedUser` deve continuar sendo carregado via `authService.getUser()`.
- `search()` deve continuar injetando `user` e `group` como parametros.
- `toggleAccess()` deve continuar enviando `granted`, `group` e `user`.
- `displayedColumns` deve permanecer coerente com a tabela.

## Fluxo atual

1. O componente recebe um grupo do pai.
2. `search()` busca o usuario logado.
3. `search()` limpa parametros e envia `user` e `group`.
4. `super.search()` reaplica `paramsOnInit` e carrega a tabela.
5. `toggleAccess()` chama a rota `grant` e recarrega a listagem.

## Exemplo de criacao de componente semelhante

```ts
export class FeaturePermissionComponent extends BaseComponentListDirective<FeatureFlag> {
    public tenant = input.required<Tenant>();
    public loggedUser = signal<User | null>(null);
    public displayedColumns = ['feature', 'access'];

    constructor(
        public injector: Injector,
        public authService: AuthService
    ) {
        super(injector, {
            endpoint: URLS.FEATURE_FLAG,
            searchOnInit: true,
            searchRoute: 'with_granted',
        });
    }

    public override async search(restartIndex = false) {
        this.loggedUser.set(await this.authService.getUser());
        this.service.clearParameter()
            .addParameter('tenant', this.tenant()?.id)
            .addParameter('user', this.loggedUser()?.id);
        super.search(restartIndex);
    }
}
```

## Exemplo de edicao segura

Para adicionar um filtro extra por modulo:

```ts
this.service
    .clearParameter()
    .addParameter('user', this.loggedUser()?.id ?? null)
    .addParameter('group', this.group()?.id ?? null)
    .addParameter('module', selectedModuleId ?? null);
```

Cuidados:

- Nao remover `group` e `user`, porque a API depende desses parametros.
- Revisar se `paramsOnInit.expand` continua valido.
- Nao transformar `search()` em fluxo puramente sincrono se `getUser()` continuar assincromo.

## Checklist para IA

- O grupo de entrada sempre existe antes da busca?
- O usuario logado esta sendo carregado antes da chamada?
- O payload de `grant` continua com os tres campos corretos?
- A listagem recarrega apos toggle?
- Os nomes dos campos da tabela ainda refletem `ModuleMenu`?

## Prompt recomendado para IA

```text
Edite o MenuPermissionComponent preservando o fluxo de permissoes por grupo.
- manter InputSignal<Group> como entrada obrigatoria
- manter busca de usuario logado via AuthService
- manter searchRoute with_granted
- enviar user e group em search()
- enviar granted, group e user em toggleAccess()
- nao substituir BaseComponentListDirective por fluxo HTTP manual
```
