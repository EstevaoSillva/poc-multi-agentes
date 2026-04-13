# GroupUserDialogComponent

**Descrição**: Este documento orienta a IA a criar e editar o `GroupUserDialogComponent`, responsável por listar usuários não associados e permitir associação ao grupo.

## Objetivo

Este guia documenta como a IA deve criar e editar [`GroupUserDialogComponent`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/group/group-user/group-user-dialog/group-user-dialog.component.ts), usado para listar usuarios nao associados e permitir associacao ao grupo dentro de um dialogo.

## Responsabilidades reais

- Receber um `Group` via `MAT_DIALOG_DATA`.
- Herdar de `BaseComponentListDirective<User>`.
- Buscar usuarios nao associados em `find_group_associated`.
- Definir `target` com `data.id`.
- Manter `paramsOnInit` com `associated: false` e `is_active: true`.
- Criar um `FormGroup` simples com `source`, `target` e `associated`.
- Disponibilizar `userService` via `createService(User, URLS.USER)`.

## Contrato que a IA deve preservar

- `data` deve continuar representando o grupo atual.
- `search()` deve reenviar `target` a partir de `data.id`.
- `BASE_OPTIONS.paramsOnInit.associated` deve continuar `false` para listar candidatos a associacao.
- `formGroup` deve continuar refletindo o payload esperado na tela.
- O componente deve continuar sendo standalone e dialog-friendly.

## Fluxo atual

1. O dialogo recebe o grupo.
2. `ngOnInit()` chama a base e depois cria o formulario.
3. `search()` filtra usuarios nao associados ao grupo.
4. A tela usa a listagem para acionar associacoes.

## Exemplo de criacao de dialogo parecido

```ts
export class TeamUserDialogComponent extends BaseComponentListDirective<User> {
    public data: Team = inject<Team>(MAT_DIALOG_DATA);
    private formBuilder = inject(FormBuilder);
    public formGroup: FormGroup;

    constructor(public injector: Injector) {
        super(injector, {
            endpoint: URLS.USER,
            associativeRoute: 'associate_team',
            searchRoute: 'find_team_associated',
            searchOnInit: true,
            paramsOnInit: { ordering: 'name', is_active: true, associated: false },
        });
    }

    public override ngOnInit(): void {
        super.ngOnInit();
        this.createFormGroup();
    }

    public createFormGroup(): void {
        this.formGroup = this.formBuilder.group({
            source: [null],
            target: [null, this.data.id],
            associated: [false],
        });
    }
}
```

## Exemplo de edicao segura

Para adicionar filtro por username:

```ts
this.service.clearParameter();
this.service.addParameter('target', this.data.id);
this.service.addParameter('username', typedUsername);
super.search(restartIndex);
```

Cuidados:

- Nao remova `target`.
- Nao troque `associated: false` se o objetivo continuar sendo listar usuarios nao associados.
- Nao remova `createFormGroup()` se o template ou a acao do dialogo dependerem dele.

## Checklist para IA

- O dialogo continua recebendo `Group` corretamente?
- A busca continua listando apenas usuarios nao associados?
- `formGroup` ainda esta alinhado ao payload de associacao?
- `userService` ainda e necessario ou pode ser mantido para fluxo futuro sem conflito?

## Prompt recomendado para IA

```text
Edite o GroupUserDialogComponent preservando o fluxo de associacao de usuarios em dialogo.
- manter MAT_DIALOG_DATA como Group
- manter BaseComponentListDirective<User>
- manter searchRoute find_group_associated com associated: false
- manter target baseado em data.id
- preservar createFormGroup com source, target e associated
```
