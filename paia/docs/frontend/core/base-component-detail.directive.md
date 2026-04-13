# BaseComponentDetailDirective

**Descrição**: Este documento orienta a IA a criar e editar componentes de formulário baseados em `BaseComponentDetailDirective<T>`.

## Objetivo

Este guia orienta a IA a criar e editar componentes de formulario baseados em [`BaseComponentDetailDirective<T>`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/base-component-detail.directive.ts).

A diretiva padroniza construcao de `FormGroup`, carga inicial do registro, persistencia, mudanca entre modo create/update, controle de campos e validacao de salvamento.

## Quando usar

Use esta base quando a tela tiver:

- formulario reativo Angular
- modo criar e editar na mesma rota
- leitura de `:action` na URL
- `save`, `update` ou envio `multipart/form-data`
- controle de habilitacao e desabilitacao de campos

Se a tela for apenas de listagem, a IA nao deve usar esta base.

## Responsabilidades reais da classe

- Criar `FormBuilder` e exigir implementacao de `createFormGroup()`.
- Executar `retrieve()` no `ngOnInit()` quando `retrieveOnInit` estiver ativo.
- Resolver ID ou modo `create` via rota.
- Salvar ou atualizar com payload normal ou `FormData`.
- Resetar o formulario com a resposta do backend.
- Navegar para `nextRoute` ou `nextRouteUpdate` apos persistencia.
- Alternar a URL entre `create` e `<id>`.
- Expor utilitarios para habilitar, desabilitar e resetar controles.

## Contrato de configuracao que a IA deve respeitar

`BaseDetailComponentOptions` inclui:

- `endpoint`: obrigatorio.
- `pk`: padrao `id`.
- `retrieveOnInit`: busca o objeto ao iniciar.
- `retrieveRoute`: rota customizada de detalhe.
- `nextRoute`: navega apos salvar ou atualizar.
- `nextRouteUpdate`: apos salvar muda para update; apos atualizar navega.
- `noResponse`: ignora comportamento padrao de resposta.
- `paramsOnInit`: envia parametros antes de recuperar o registro.

## Sequencia correta de inicializacao

Ao criar um componente filho, a IA deve manter esta sequencia:

1. Chamar `super.ngOnInit()`.
2. Criar o `FormGroup` em `createFormGroup()`.
3. Se `retrieveOnInit` estiver ativo, deixar a base chamar `retrieve()`.
4. Deixar `_response()` popular `object`, `rawObject` e o formulario.

Nao mova a criacao do formulario para depois do `retrieve()`, porque a base faz `formGroup.reset(this.object)` quando recebe resposta.

## Exemplo de criacao de formulario

```ts
import { Component, Injector } from '@angular/core';
import { Validators } from '@angular/forms';
import { BaseComponentDetailDirective } from '../base-component-detail.directive';

interface UserDetail {
    id?: number;
    username: string;
    email: string;
    active: boolean;
}

@Component({
    selector: 'app-user-detail',
    templateUrl: './user-detail.component.html',
})
export class UserDetailComponent extends BaseComponentDetailDirective<UserDetail> {
    constructor(public override injector: Injector) {
        super(injector, {
            endpoint: '/api/users/',
            formTitle: 'Usuario',
            retrieveOnInit: true,
            nextRouteUpdate: '/users/:action',
            pk: 'id',
        });
    }

    public createFormGroup(): void {
        this.formGroup = this.formBuilder.group({
            id: [null],
            username: [null, [Validators.required]],
            email: [null, [Validators.required, Validators.email]],
            active: [true],
        });
    }
}
```

## Exemplo de edicao com dependencia entre campos

Se a IA precisar habilitar um campo apenas quando outro estiver marcado:

```ts
public override createFormGroup(): void {
    this.formGroup = this.formBuilder.group({
        hasDeadline: [false],
        deadline: [{ value: null, disabled: true }],
    });

    this.handleField(
        this.f['hasDeadline'],
        this.f['deadline'],
        (value) => Boolean(value)
    );
}
```

## Exemplo de save/update simples

```ts
public submit(): void {
    if (!this.isFormValidSave) {
        this.toast.warning('warning', this.isFormValidSaveMessage);
        return;
    }

    this.saveOrUpdate();
}
```

## Exemplo de envio com arquivo

```ts
public saveAttachment(): void {
    this.saveOrUpdateFormData();
}
```

Regras para a IA:

- Use `saveOrUpdateFormData()` somente quando houver `File` ou `FileList`.
- Nao monte `FormData` manualmente fora da base sem necessidade.
- Campos `null` ou `undefined` ja sao tratados pela diretiva.

## Exemplo de criacao de projeto com detalhe

Ao gerar um novo formulario CRUD, a IA deve seguir este roteiro:

1. Criar componente `XDetailComponent` herdando da diretiva.
2. Declarar `options` com `endpoint`, `retrieveOnInit`, `pk` e rota de retorno.
3. Implementar `createFormGroup()`.
4. Ler `this.f`, `this.v` e `this.rv` em vez de acessar controles manualmente em todo lugar.
5. Chamar `saveOrUpdate()` ou `saveOrUpdateFormData()` no submit.
6. Reusar `enableControls()`, `disableControls()` e `resetAndDisableControls()` em fluxos condicionais.

## Regras de rota que a IA nao deve quebrar

- O modo de edicao e determinado pelo parametro `action`.
- Quando `action === 'create'`, `beforeRetrieve()` retorna `null`.
- Ao salvar um novo registro com `nextRouteUpdate`, a base troca `:action` pelo ID real.
- Ao voltar para create mode, a base troca `:action` por `create`.

## Checklist de edicao para IA

- `createFormGroup()` cria todos os controles esperados pela API?
- `retrieveOnInit` esta coerente com a rota da tela?
- O formulario e resetado pela resposta da API sem perder campos?
- O submit usa `saveOrUpdate*()` em vez de chamar servico diretamente?
- Validacao de botao salvar usa `isFormValidSave` e `isFormValidSaveMessage`?
- Campos condicionais usam `handleField()` ou metodos equivalentes da base?

## Prompt recomendado para IA

```text
Crie ou edite um formulario Angular herdando de BaseComponentDetailDirective.
Siga o contrato do projeto:
- implementar createFormGroup()
- usar retrieveOnInit quando houver modo editar
- usar saveOrUpdate(), saveOrUpdatePlus(), saveOrUpdateFormData() ou saveOrUpdateFormDataPlus()
- manter comportamento de create/update baseado na rota :action
- reutilizar enableControls, disableControls, resetAndDisableControls e handleField
- nao duplicar logica de FormData, retrieve ou navegacao de retorno
Inclua exemplos de criacao e edicao de CRUD seguindo o estilo atual do repositorio.
```

## Erros comuns que a IA deve evitar

- Preencher o formulario sem chamar `createFormGroup()` antes.
- Fazer `patchValue` manual em todos os fluxos e ignorar `_response()`.
- Chamar `service.save()` ou `service.update()` direto no componente sem aproveitar a base.
- Esquecer que `isFormValidSave` exige formulario valido e alterado.
- Mudar o nome do parametro de rota esperado pela base sem ajustar o restante do fluxo.
