# Guia de Construção do Componente de Autenticação

**Descrição**: Este documento orienta a IA a recriar ou evoluir a feature visual de autenticação do frontend com Angular moderno, preservando o comportamento funcional do fluxo de login.

## Objetivo

Este guia descreve como uma IA deve recriar o fluxo de autenticacao analisado em [`src/app/components/auth`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/auth), mas usando abordagem moderna de mercado para Angular 19:

- componentes `standalone`
- roteamento com `loadComponent`
- estado local com `signal`
- derivacoes com `computed`
- efeitos com `effect` quando fizer sentido
- injecao com `inject(...)`
- template control flow moderno como `@if`

O objetivo nao e copiar a implementacao legada. O objetivo e reproduzir o mesmo comportamento com a stack mais atual do ecossistema Angular.

## Base técnica observada no projeto

O repositorio usa Angular 19, RxJS 7 e Angular Material. Portanto, a IA deve considerar como baseline:

- Angular `^19.2.0`
- Material `^19.2.0`
- `standalone` como padrao
- `signals` como primeira opcao para estado de UI
- `ReactiveFormsModule` para formulario
- `provideRouter` e rotas lazy sempre que possivel

## Arquivos reais usados apenas como referencia funcional

- [`auth.module.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/auth/auth.module.ts)
- [`auth.route.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/auth/auth.route.ts)
- [`login.component.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/auth/login/login.component.ts)
- [`login.component.html`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/auth/login/login.component.html)
- [`login.component.scss`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/auth/login/login.component.scss)
- [`auth.service.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/services/auth.service.ts)
- [`app.guard.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/app.guard.ts)

Esses arquivos representam o comportamento existente. A nova versao orientada por IA deve preservar o fluxo, nao a forma antiga.

## O que a IA deve construir

A IA deve gerar estas pecas:

- uma feature de autenticacao sem `NgModule`
- uma rota lazy para `signin`
- um componente standalone de entrada
- um servico de sessao separado da UI
- um guard funcional ou `CanActivateFn`
- estado de UI com `signal`
- integracao com traducao
- redirecionamento apos login
- validacao de sessao antes de interacao

## Nomes de exemplo obrigatorios

Para nao copiar o dominio real, a IA deve usar nomes neutros como:

- `SignInPageComponent`
- `SessionService`
- `session.routes.ts`
- `session.guard.ts`
- `AccountCredentials`
- `WorkspaceOption`
- `Example Suite`
- `example-logo.svg`

Nao usar nomes reais do produto, empresa, endpoints ou modelos originais.

## Mapeamento do legado para a versao moderna

- `AuthModule` vira rota standalone, sem modulo.
- `ROUTES` continua existindo, mas em arquivo de feature lazy.
- `LoginComponent` vira `SignInPageComponent` standalone.
- `AuthService` continua existindo conceitualmente, mas com nome generico como `SessionService`.
- estados booleanos e textos mutaveis deixam de ser propriedades simples e viram `signal`.
- dependencias deixam de ser injetadas via construtor e passam a usar `inject`.

## Responsabilidades que a IA deve preservar

### Rota

- Expor uma rota como `signin`.
- Usar `loadComponent` para lazy loading do componente.
- Aplicar guard funcional quando a arquitetura exigir.
- Preservar query param de retorno, como `redirect`.

### Componente standalone

- Declarar `standalone: true`.
- Importar explicitamente os modulos e componentes necessarios no array `imports`.
- Criar formulario reativo tipado.
- Ler query param de retorno.
- Verificar sessao ativa no carregamento.
- Submeter credenciais pelo servico.
- Exibir loading durante autenticacao.
- Limpar o campo secreto em caso de falha.
- Redirecionar ao concluir o login.
- Permitir mostrar ou ocultar a senha.
- Integrar traduzivel por chave.

### Estado local

- Usar `signal(false)` para `loading`.
- Usar `signal(true)` para `hideSecret`.
- Usar `signal('sign-in')` para o texto do CTA.
- Usar `computed(() => ...)` para derivar `submitDisabled`.
- Usar `signal('/')` para `returnUrl`.
- Evitar estado mutavel avulso em propriedades simples se ele puder ser modelado por signal.

### Servico

- Concentrar autenticacao, logout, tokens e leitura de sessao.
- Usar `providedIn: 'root'`.
- Encapsular persistencia de token.
- Encapsular leitura de token e decode de payload.
- Expor `login`, `logout`, `isLoggedIn`, `setToken`, `clearSession`.
- Pode expor sinal global de sessao se a feature precisar refletir estado autenticado em outras areas.

## Padroes modernos obrigatorios

- Preferir `inject()` em vez de construtor com muitos parametros.
- Preferir `signal`, `computed` e `effect` para estado de apresentacao.
- Preferir `CanActivateFn` a classes de guard quando nao houver necessidade real de classe.
- Preferir `loadComponent` em vez de carregar feature module.
- Preferir `async/await` apenas nas bordas necessarias; manter streams HTTP no servico com RxJS.
- Preferir `take(1)` ou `firstValueFrom` apenas quando houver motivo claro.
- Preferir `DestroyRef` com `takeUntilDestroyed` em assinaturas de ciclo de vida.
- Preferir control flow nativo do Angular, como `@if`, em vez de `*ngIf`.

## O que evitar

- Nao criar `NgModule` novo para essa feature.
- Nao usar `EventEmitter` para estado interno de UI.
- Nao colocar `HttpClient` diretamente no componente.
- Nao usar propriedades soltas quando `signal` cobre melhor o caso.
- Nao depender de `subscribe` espalhado sem controle de ciclo de vida.
- Nao misturar nome real do dominio com nome ficticio.
- Nao usar abordagem antiga so porque o legado usa.

## Fluxo funcional que deve continuar igual

1. Usuario acessa a rota `signin`.
2. O componente inicializa o formulario.
3. O componente resolve a URL de retorno por query param.
4. O componente verifica se a sessao ja existe.
5. Se a sessao ja existir, redireciona imediatamente.
6. Se nao existir, exibe tela de autenticacao.
7. O usuario informa `login` e `secret`.
8. O componente chama `SessionService.login(...)`.
9. O servico persiste tokens.
10. O componente navega para a URL de retorno.

## Contrato tecnico minimo

- formulario reativo com `login` e `secret` obrigatorios
- correspondencia exata entre `formControlName` e controles do formulario
- `SessionService` como unica camada que grava e limpa token
- checagem de sessao antes de permitir uso normal da tela
- tratamento de erro com limpeza do segredo digitado
- botao de submit desabilitado durante loading ou formulario invalido
- integracao com traducoes por chave
- layout centralizado em tela cheia

## Exemplo de rotas modernas

```ts
// session.routes.ts
import { Routes } from '@angular/router';
import { signedOutGuard } from './session.guard';

export const sessionRoutes: Routes = [
    {
        path: 'signin',
        canActivate: [signedOutGuard],
        loadComponent: () =>
            import('./sign-in-page.component').then((m) => m.SignInPageComponent),
    },
];
```

## Exemplo de guard funcional

```ts
// session.guard.ts
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SessionService } from './session.service';

export const signedOutGuard: CanActivateFn = async (route) => {
    const router = inject(Router);
    const sessionService = inject(SessionService);
    const redirect = route.queryParamMap.get('redirect') || '/';

    if (await sessionService.isLoggedIn()) {
        return router.createUrlTree([redirect]);
    }

    return true;
};
```

## Exemplo de componente standalone com signals

```ts
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { take } from 'rxjs/operators';

@Component({
    selector: 'app-sign-in-page',
    standalone: true,
    templateUrl: './sign-in-page.component.html',
    styleUrl: './sign-in-page.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [
        ReactiveFormsModule,
        MatButtonModule,
        MatCardModule,
        MatFormFieldModule,
        MatIconModule,
        MatInputModule,
    ],
})
export class SignInPageComponent {
    private readonly fb = inject(FormBuilder);
    private readonly route = inject(ActivatedRoute);
    private readonly router = inject(Router);
    private readonly sessionService = inject(SessionService);

    readonly loading = signal(false);
    readonly hideSecret = signal(true);
    readonly ctaKey = signal('sign-in');
    readonly returnUrl = signal('/');

    readonly form = this.fb.nonNullable.group({
        login: ['', Validators.required],
        secret: ['', Validators.required],
    });

    readonly submitDisabled = computed(() => this.loading() || this.form.invalid);

    async ngOnInit(): Promise<void> {
        this.returnUrl.set(this.route.snapshot.queryParamMap.get('redirect') || '/');

        if (await this.sessionService.isLoggedIn()) {
            await this.router.navigateByUrl(this.returnUrl());
        }
    }

    async submit(): Promise<void> {
        if (this.form.invalid || this.loading()) return;

        this.loading.set(true);
        this.ctaKey.set('loading');

        const credentials = this.form.getRawValue();

        (await this.sessionService.login(credentials)).pipe(take(1)).subscribe({
            next: async () => {
                await this.router.navigateByUrl(this.returnUrl());
            },
            error: () => {
                this.loading.set(false);
                this.ctaKey.set('sign-in');
                this.form.controls.secret.reset();
            },
        });
    }

    toggleSecretVisibility(): void {
        this.hideSecret.update((value) => !value);
    }
}
```

## Exemplo de template moderno

```html
<section class="entry-screen">
    <div class="brand-block">
        <img src="assets/example-logo.svg" alt="Example Suite" width="220" height="72" />
    </div>

    <form class="entry-form" [formGroup]="form" (ngSubmit)="submit()">
        <mat-card class="entry-card">
            <mat-card-title>{{ 'welcome' | translate }}</mat-card-title>
            <mat-card-subtitle>{{ 'please-sign-in' | translate }}</mat-card-subtitle>

            <mat-form-field appearance="outline">
                <mat-label>{{ 'login' | translate }}</mat-label>
                <input matInput formControlName="login" maxlength="64" required />
                @if (form.controls.login.hasError('required')) {
                    <mat-error>{{ 'field-required' | translate }}</mat-error>
                }
            </mat-form-field>

            <mat-form-field appearance="outline">
                <mat-label>{{ 'secret' | translate }}</mat-label>
                <input
                    matInput
                    [type]="hideSecret() ? 'password' : 'text'"
                    formControlName="secret"
                    maxlength="128"
                    required
                />
                <button mat-icon-button matSuffix type="button" (click)="toggleSecretVisibility()">
                    <mat-icon>{{ hideSecret() ? 'visibility_off' : 'visibility' }}</mat-icon>
                </button>
                @if (form.controls.secret.hasError('required')) {
                    <mat-error>{{ 'field-required' | translate }}</mat-error>
                }
            </mat-form-field>

            <button mat-raised-button color="primary" type="submit" [disabled]="submitDisabled()">
                @if (loading()) {
                    <span class="spinner-border spinner-border-sm"></span>
                }
                {{ ctaKey() | translate }}
            </button>
        </mat-card>
    </form>
</section>
```

## Exemplo de servico moderno

```ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class SessionService {
    private readonly http = inject(HttpClient);
    private readonly storage = localStorage;
    private readonly accessTokenKey = 'example_access_token';
    private readonly refreshTokenKey = 'example_refresh_token';

    login(credentials: AccountCredentials) {
        return this.http.post<SessionResponse>('/api/session/token/', credentials).pipe(
            tap((response) => this.setToken(response))
        );
    }

    async isLoggedIn(): Promise<boolean> {
        const token = this.storage.getItem(this.accessTokenKey)?.trim();
        return !!token && token.split('.').length === 3;
    }

    logout(): void {
        this.clearSession();
    }

    private setToken(response: SessionResponse): void {
        this.storage.setItem(this.accessTokenKey, response.token.access);
        this.storage.setItem(this.refreshTokenKey, response.token.refresh);
    }

    private clearSession(): void {
        this.storage.removeItem(this.accessTokenKey);
        this.storage.removeItem(this.refreshTokenKey);
    }
}
```

## Estado recomendado para a UI

Use `signal` para estado efemero da tela:

- `loading`
- `hideSecret`
- `ctaKey`
- `returnUrl`
- lista de `workspaceOptions`, se a tela realmente exibir isso

Use `computed` para:

- `submitDisabled`
- titulo derivado
- mensagens visuais simples dependentes de estado

Use `effect` apenas quando houver efeito colateral claro, por exemplo:

- reagir a mudanca de idioma e sincronizar locale
- reagir a sessao autenticada e navegar

Nao usar `effect` para logica que pode ficar em metodo explicito de submit.

## Regras visuais

- container principal com `min-height: 100vh`
- fundo visual forte, mas legivel
- card central com largura maxima controlada
- logo acima do card
- inputs empilhados
- CTA principal ocupando largura util
- visual responsivo para mobile e desktop

## Dependencias esperadas na solucao gerada

- `@angular/core`
- `@angular/router`
- `@angular/forms`
- `@angular/material`
- `rxjs`
- servico de traducao do projeto
- cliente HTTP

## Prompt recomendado para IA

```text
Crie uma feature de autenticacao em Angular 19 inspirada no fluxo de login deste projeto, mas implementada com padrao moderno.

Use obrigatoriamente:
- componente standalone
- rotas com loadComponent
- inject() em vez de construtor extenso
- estado local com signal
- derivacoes com computed
- control flow moderno no template
- formulario reativo tipado
- servico de sessao separado da UI
- nomes neutros como SignInPageComponent, SessionService e Example Suite

Preserve o comportamento:
- rota de signin
- login com campos obrigatorios
- leitura de query param redirect
- redirecionamento se ja estiver autenticado
- persistencia de tokens no servico
- limpeza do segredo em erro
- CTA de loading
- layout centralizado em tela cheia

Evite:
- NgModule
- nomes reais do projeto
- HttpClient no componente
- estado local sem signal
- copiar a implementacao legada literalmente
```

## Checklist para a IA

- a feature ficou sem `NgModule`?
- a rota usa `loadComponent`?
- o componente e `standalone: true`?
- o estado da UI usa `signal`?
- existe `computed` para derivar estado do botao?
- o servico centraliza token e sessao?
- os nomes sao todos genericos?
- o template usa `hideSecret()` e `loading()` em vez de propriedades mutaveis soltas?
- o formulario e reativo e tipado?
- o fluxo de redirect foi preservado?

## Erros comuns que a IA deve evitar

- recriar a estrutura antiga com `AuthModule`
- usar `boolean` simples quando o estado pede `signal`
- usar construtor inchado em vez de `inject`
- misturar nomes genericos e nomes reais
- esquecer o query param `redirect`
- deixar o botao habilitado durante loading
- nao limpar o segredo quando o login falhar
- usar `subscribe` permanente para algo pontual
