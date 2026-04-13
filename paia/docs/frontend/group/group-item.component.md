# GroupItemComponent

**Descrição**: Este documento orienta a IA a criar e editar o `GroupItemComponent`, responsável pela tela de detalhe e edição de grupos.

## Objetivo

Este guia documenta como a IA deve criar e editar [`GroupItemComponent`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/group/group-item/group-item.component.ts), que representa a tela de detalhe e edicao de um grupo.

O componente herda de `BaseComponentDetailDirective<Group>` e integra o formulario do grupo com subcomponentes de usuarios e permissoes.

## Responsabilidades reais

- Recuperar um grupo com `retrieveOnInit: true`.
- Exibir e editar o campo `name`.
- Controlar um modo de edicao local via `editMode`.
- Desabilitar o formulario quando o grupo ja existe.
- Reaproveitar `GroupUserComponent` e `MenuPermissionComponent`.
- Salvar, atualizar e excluir grupos.

## Contrato que a IA deve preservar

- O componente deve continuar herdando de `BaseComponentDetailDirective<Group>`.
- `endpoint` deve permanecer em `URLS.GROUP`.
- `formTitle` deve continuar usando `group-management`.
- `createFormGroup()` deve continuar criando o controle `name`.
- Quando `object.url` existir no callback do `ngOnInit`, o formulario deve ser desabilitado.
- `saveOrUpdate()` customizado deve continuar desligando `editMode` e desabilitando `name`.

## Fluxo atual que a IA deve entender

1. `super.ngOnInit()` cria o formulario e recupera o grupo.
2. No callback, se o objeto ja existe, `formGroup.disable()`.
3. `onEditMode()` alterna a habilitacao do campo `name`.
4. `saveOrUpdate()` chama a base e depois volta a tela ao modo bloqueado.
5. `delete()` confirma e exclui, depois navega para `WEB.GROUP`.

## Exemplo de criacao de detalhe semelhante

```ts
export class DepartmentItemComponent extends BaseComponentDetailDirective<Department> {
    public object: Department = new Department();
    public editMode = false;

    constructor(public injector: Injector) {
        super(injector, {
            pk: 'id',
            endpoint: URLS.DEPARTMENT,
            formRoute: WEB.DEPARTMENT,
            retrieveOnInit: true,
            formTitle: 'department-management',
        });
    }

    public override ngOnInit(): void {
        super.ngOnInit(() => {
            if (this.object.url) {
                this.formGroup.disable();
            }
        });
    }

    public createFormGroup(): void {
        this.formGroup = this.formBuilder.group({
            name: [{ value: null, disabled: this.editMode }, CustomValidators.required],
        });
    }
}
```

## Exemplo de edicao segura

Se a IA precisar adicionar o campo `description`:

```ts
public createFormGroup(): void {
    this.formGroup = this.formBuilder.group({
        name: [{ value: null, disabled: this.editMode }, CustomValidators.required],
        description: [{ value: null, disabled: this.editMode }],
    });
}
```

Regras:

- Ajustar o template para refletir o novo campo.
- Atualizar o modelo `Group` se o backend realmente retornar esse valor.
- Incluir o novo controle na logica de habilitar/desabilitar se necessario.

## Cuidados especificos para IA

- `editMode` controla comportamento visual e de permissao local; nao remova isso sem revisar a UX.
- `delete()` usa `confirm()` da base; nao crie outro dialogo de exclusao sem necessidade.
- O componente incorpora `GroupUserComponent` e `MenuPermissionComponent`; mudancas no fluxo do grupo podem impactar esses filhos.

## Checklist para IA

- O formulario continua compatível com o contrato do backend?
- Os campos habilitados em edit mode estao corretos?
- O callback de `saveOrUpdate()` continua restaurando o estado bloqueado?
- A exclusao continua retornando para `WEB.GROUP`?
- Os componentes filhos ainda recebem um `Group` valido?

## Prompt recomendado para IA

```text
Edite o GroupItemComponent preservando o comportamento de detalhe do grupo.
- manter heranca de BaseComponentDetailDirective<Group>
- manter retrieveOnInit e endpoint URLS.GROUP
- manter controle local de editMode
- preservar a desabilitacao do formulario quando o grupo ja existe
- reaproveitar saveOrUpdate() da base e confirm() para delete
- considerar impacto em GroupUserComponent e MenuPermissionComponent
```
