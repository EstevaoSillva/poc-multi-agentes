# BaseComponentCommons

**Descrição**: Este documento orienta a IA a criar, editar e reutilizar a base compartilhada `BaseComponentCommons<T>` para componentes Angular do projeto.

## Objetivo

Este arquivo documenta como uma IA deve criar, editar e reutilizar [`BaseComponentCommons<T>`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/base-component-commons.ts) como base para componentes Angular do projeto.

O papel desta classe e concentrar dependencias comuns, navegacao, confirmacao, historico, foco, titulo de pagina e criacao dinamica de servicos.

## Responsabilidades reais da classe

- Resolver dependencias compartilhadas via `Injector`.
- Criar `BaseService<T>` dinamicamente a partir de `options.endpoint`.
- Padronizar confirmacoes e historico.
- Facilitar navegacao relativa e absoluta.
- Expor utilitarios de foco, titulo e rota.
- Centralizar descarte com `unsubscribe`.

## Contrato esperado pela IA

Ao criar ou editar componentes que herdam esta classe, a IA deve preservar estes pontos:

- `options.endpoint` e obrigatorio.
- `options.pk` e opcional; o padrao e `id`.
- `serviceToken()` precisa continuar produzindo um `InjectionToken<BaseService<T>>`.
- `confirm()` deve continuar retornando `Observable<boolean>`.
- `history()` depende de `this.object[this.pk]` quando `pk` nao e informado.
- `goToPage()` aceita rota como `string` ou `string[]`.
- `ngOnDestroy()` deve continuar emitindo e completando `unsubscribe`.

## Como a IA deve usar esta base

Ao criar um novo componente, a IA deve:

1. Herdar de `BaseComponentCommons<T>` apenas se o componente precisar de comportamento comum, mas nao de tabela nem formulario.
2. Passar `Injector` e `options` no `super(...)`.
3. Definir `endpoint`, `formTitle`, `formRoute` e `pk` somente quando fizer sentido para o recurso.
4. Reaproveitar `createService()` para servicos auxiliares, em vez de criar `HttpClient` manualmente.
5. Usar `confirm()` para operacoes destrutivas ou sensiveis.
6. Usar `goToPage()` para navegacao, respeitando `queryParamsHandling: 'merge'`.

## Exemplo de criacao de componente

```ts
import { Component, Injector } from '@angular/core';
import { BaseComponentCommons } from './base-component-commons';

interface ReportSummary {
    id: number;
    name: string;
    active: boolean;
}

@Component({
    selector: 'app-report-summary',
    templateUrl: './report-summary.component.html',
})
export class ReportSummaryComponent extends BaseComponentCommons<ReportSummary> {
    constructor(public override injector: Injector) {
        super(injector, {
            endpoint: '/api/report-summary/',
            formTitle: 'Relatorio',
            formRoute: '/report-summary',
            pk: 'id',
        });
    }

    closeAndReturn(): void {
        this.goToPage('/report-summary');
    }
}
```

## Exemplo de edicao segura

Se a IA precisar adicionar uma acao de confirmacao antes de sair da tela:

```ts
public closeWithConfirmation(): void {
    this.confirm('confirm', 'Deseja sair da tela?')
        .pipe(take(1))
        .subscribe((confirmed) => {
            if (confirmed) {
                this.goToPage(this.formRoute || '/');
            }
        });
}
```

Diretrizes para a IA nessa edicao:

- Nao duplicar `MatDialog` no componente filho.
- Nao recriar `Router` manualmente.
- Nao ignorar `formRoute` se ele ja estiver configurado.

## Exemplo de uso de servico auxiliar

```ts
const auditService = this.createService(AuditItem, '/api/audit-item/');
auditService.getAll().pipe(take(1)).subscribe();
```

Boas praticas para a IA:

- Criar servicos auxiliares somente quando o endpoint secundario for realmente distinto.
- Manter o endpoint principal em `options.endpoint`.
- Nao sobrescrever `this.service` sem necessidade.

## Regras de navegacao que a IA deve respeitar

- Quando a rota vier como `'/a/b/c'`, `goToPage()` quebra em segmentos absolutos.
- Quando a rota vier como `'detail'`, a navegacao e relativa ao contexto atual apenas se `relativeToCurrent` for `true`.
- Parametros de query devem ser mesclados quando enviados.

## Regras de estado que a IA nao deve quebrar

- `object` funciona como estado corrente do recurso.
- `pk` controla o identificador primario usado por classes filhas.
- `unsubscribe` e o mecanismo padrao de limpeza do projeto.
- `changeTitlePage()` deve continuar emitindo em `main.changeTitle`.

## Checklist de implementacao para IA

- A classe filha precisa mesmo desta base ou precisa de `BaseComponentListDirective`?
- O `endpoint` aponta para o recurso correto?
- O `pk` foi mantido coerente com a API?
- A navegacao usa `goToPage()` em vez de `router.navigate(...)` espalhado?
- A confirmacao usa `confirm()` em vez de dialogo duplicado?
- Fluxos assincronos longos usam `takeUntil(this.unsubscribe)`?

## Prompt recomendado para IA

```text
Crie ou edite um componente Angular herdando de BaseComponentCommons.
Preserve o contrato atual do projeto:
- usar super(injector, { endpoint, formTitle, formRoute, pk })
- reutilizar this.service ou createService()
- usar goToPage() para navegacao
- usar confirm() para confirmacoes
- nao quebrar unsubscribe no ngOnDestroy
- manter object como estado principal
Explique no codigo somente o necessario e siga o estilo existente do repositorio.
```

## Erros comuns que a IA deve evitar

- Instanciar `BaseService` diretamente no componente filho sem passar pela base.
- Duplicar `Injector.get(...)` para dependencias ja expostas.
- Chamar `window.history.back()` quando a navegacao padrao do projeto usa rotas explicitas.
- Ignorar `take(1)` ou `takeUntil(this.unsubscribe)` em observables de UI.
- Mudar o retorno de `confirm()` ou o comportamento de `history()`.
