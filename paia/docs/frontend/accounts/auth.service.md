# Guia de Construção do Service de Autenticação

**Descrição**: Este documento orienta a IA a recriar ou evoluir o service de autenticação e sessão do frontend com Angular moderno, preservando contratos de login, refresh token e usuário autenticado.

## Objetivo

Este guia descreve como uma IA deve recriar o comportamento de [`src/app/services/auth.service.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/services/auth.service.ts) usando padrao moderno de Angular 19, com nomes de exemplo e sem copiar a implementacao legada.

O foco e preservar responsabilidades e contratos de autenticacao, mas com:

- `providedIn: 'root'`
- `inject(...)`
- API mais coesa
- tipos mais explicitos
- nomes neutros
- servico pronto para uso com componentes standalone e guards funcionais

## Papel real do servico

O servico atual concentra:

- login por endpoint de token
- persistencia de access token e refresh token
- leitura de sessao
- decode do usuario a partir do JWT
- logout
- carga de modulos permitidos
- carga de menus
- troca de senha
- suporte a refresh token
- armazenamento de modulo selecionado

## Como a IA deve reinterpretar isso

A IA deve reimplementar esse servico como um `SessionService` ou nome equivalente, com design mais moderno, mas preservando os mesmos papeis:

- autenticar credenciais
- salvar sessao
- validar se ha sessao
- expor usuario autenticado
- carregar contextos permitidos
- renovar token
- encerrar sessao

## Nomes de exemplo obrigatorios

Ao gerar uma versao equivalente, usar nomes como:

- `SessionService`
- `AccountCredentials`
- `AuthenticatedUser`
- `SessionPayload`
- `SessionResponse`
- `WorkspaceOption`
- `NavigationMenuResponse`
- `ChangeSecretPayload`

Nao usar nomes reais do produto, usuario, modulo ou endpoint.

## Contrato funcional que a IA deve preservar

- existir metodo de login que chame o endpoint de autenticacao
- existir persistencia de access token e refresh token
- existir metodo para verificar se ha sessao valida
- existir metodo para limpar a sessao
- existir metodo para logout com opcao de redirecionamento
- existir metodo para obter usuario a partir do JWT
- existir metodo para refresh do token
- existir metodo para carregar contextos ativos
- existir metodo para carregar contextos permitidos para um usuario
- existir metodo para carregar menu permitido

## Responsabilidades separadas que a IA deve manter

### Sessao

- guardar tokens
- limpar tokens
- ler tokens
- validar formato basico do JWT

### Usuario autenticado

- decodificar payload do token
- normalizar dados do usuario se a API devolver snake_case
- expor usuario atual por `signal` ou metodo

### Navegacao

- evitar navegar para rota de login se ja estiver nela
- permitir logout com redirecionamento opcional

### Contexto de aplicacao

- carregar lista de contextos ativos
- carregar lista de contextos autorizados para o usuario
- opcionalmente persistir contexto selecionado

## Padrao moderno recomendado

- `@Injectable({ providedIn: 'root' })`
- `private readonly http = inject(HttpClient)`
- `private readonly router = inject(Router)`
- `readonly currentUser = signal<AuthenticatedUser | null>(null)`
- `readonly isAuthenticated = computed(() => this.currentUser() !== null || this.hasStoredToken())`
- helpers privados para armazenamento

Se a IA optar por manter `Promise<boolean>` em `isLoggedIn()`, isso e aceitavel quando a inicializacao de chaves ou criptografia for assincrona. Se nao houver essa necessidade, pode retornar `boolean` puro.

## O que a IA deve modernizar

- trocar injecao por construtor extenso por `inject`
- tipar melhor as respostas de autenticacao
- remover `Subject<void>` de unsubscribe se ele nao for usado pelo servico
- evitar `shareReplay()` sem justificativa concreta
- centralizar parse de token em helper privado
- expor sinal de usuario atual para consumo por componentes e guards

## O que a IA nao deve quebrar

- persistencia dos dois tokens
- validacao minima do access token
- suporte a refresh token
- possibilidade de buscar usuario atual pelo JWT
- capacidade de carregar contexto autorizado do usuario
- possibilidade de redirecionamento no logout

## Estrutura sugerida para a nova API

```ts
export interface AccountCredentials {
    login: string;
    secret: string;
}

export interface SessionResponse {
    token: {
        access: string;
        refresh: string;
    };
}

export interface SessionPayload {
    sub: number;
    login: string;
    user: AuthenticatedUser;
    exp: number;
}

export interface AuthenticatedUser {
    id: number;
    login: string;
    displayName: string;
    avatarUrl?: string;
}
```

## Exemplo moderno de servico

```ts
import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Router } from '@angular/router';
import { jwtDecode } from 'jwt-decode';
import { catchError, map, of, tap } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SessionService {
    private readonly http = inject(HttpClient);
    private readonly router = inject(Router);
    private readonly storage = localStorage;

    private readonly baseUrl = '/api';
    private readonly accessTokenKey = 'example_access_token';
    private readonly refreshTokenKey = 'example_refresh_token';
    private readonly workspaceKey = 'example_workspace';

    readonly currentUser = signal<AuthenticatedUser | null>(null);
    readonly authenticated = computed(() => !!this.currentUser() || this.hasStoredToken());

    login(credentials: AccountCredentials) {
        return this.http.post<SessionResponse>(`${this.baseUrl}/session/token/`, credentials).pipe(
            tap((response) => this.setTokens(response)),
            tap(() => this.hydrateCurrentUserFromToken())
        );
    }

    logout(options?: { redirectTo?: string; reload?: boolean }): void {
        this.clearSession();

        if (options?.reload) {
            location.reload();
            return;
        }

        if (options?.redirectTo) {
            void this.router.navigateByUrl(options.redirectTo);
        }
    }

    isLoggedIn(): boolean {
        const token = this.getAccessToken();
        return !!token && token.split('.').length === 3;
    }

    getCurrentUser(): AuthenticatedUser | null {
        if (!this.currentUser()) {
            this.hydrateCurrentUserFromToken();
        }
        return this.currentUser();
    }

    refreshToken() {
        const refresh = this.getRefreshToken();
        if (!refresh) {
            return of(null);
        }

        return this.http.post<SessionResponse>(`${this.baseUrl}/session/refresh/`, { refresh }).pipe(
            tap((response) => this.setTokens(response))
        );
    }

    loadWorkspaceOptions() {
        const params = new HttpParams({ fromObject: { active: 'true' } });
        return this.http.get<WorkspaceOption[]>(`${this.baseUrl}/workspace/`, { params }).pipe(
            catchError(() => of([]))
        );
    }

    loadAllowedWorkspaceOptions(userId: number) {
        const params = new HttpParams({
            fromObject: { user: String(userId), granted: 'true', active: 'true' },
        });

        return this.http.get<WorkspaceOption[]>(`${this.baseUrl}/workspace/allowed/`, {
            headers: this.authHeaders(),
            params,
        });
    }

    loadNavigationMenu(userId: number) {
        const params = new HttpParams({ fromObject: { user: String(userId) } });
        return this.http.get<NavigationMenuResponse>(`${this.baseUrl}/workspace-menu/find-menu/`, {
            headers: this.authHeaders(),
            params,
        });
    }

    changeSecret(userId: number, payload: ChangeSecretPayload) {
        return this.http.patch<{ detail: string }>(
            `${this.baseUrl}/users/${userId}/change-secret/`,
            payload,
            { headers: this.authHeaders() }
        );
    }

    setSelectedWorkspace(workspace: WorkspaceOption): void {
        this.storage.setItem(this.workspaceKey, JSON.stringify(workspace));
    }

    clearSession(): void {
        this.storage.removeItem(this.accessTokenKey);
        this.storage.removeItem(this.refreshTokenKey);
        this.storage.removeItem(this.workspaceKey);
        this.currentUser.set(null);
    }

    private hydrateCurrentUserFromToken(): void {
        const token = this.getAccessToken();
        if (!token || token.split('.').length !== 3) {
            this.currentUser.set(null);
            return;
        }

        const payload = jwtDecode<SessionPayload>(token);
        this.currentUser.set(payload.user);
    }

    private setTokens(response: SessionResponse): void {
        this.storage.setItem(this.accessTokenKey, response.token.access);
        this.storage.setItem(this.refreshTokenKey, response.token.refresh);
    }

    private getAccessToken(): string | null {
        return this.storage.getItem(this.accessTokenKey)?.trim() ?? null;
    }

    private getRefreshToken(): string | null {
        return this.storage.getItem(this.refreshTokenKey)?.trim() ?? null;
    }

    private hasStoredToken(): boolean {
        return !!this.getAccessToken();
    }

    private authHeaders(): HttpHeaders {
        return new HttpHeaders({
            Authorization: `Bearer ${this.getAccessToken() ?? ''}`,
        });
    }
}
```

## Decisoes que a IA deve tomar corretamente

- usar `signal` para o usuario atual quando o app precisa refletir sessao em tempo real
- manter `Observable` para chamadas HTTP
- usar helper privado para headers autenticados
- encapsular storage para nao espalhar chaves de sessao no app

## Integracao esperada com componentes standalone

Componentes como `SignInPageComponent` devem:

- chamar `sessionService.login(credentials)`
- reagir ao sucesso navegando para a rota de retorno
- nunca gravar token diretamente
- consultar `sessionService.isLoggedIn()` ou `sessionService.currentUser()`

## Integracao esperada com guards funcionais

Guards devem:

- injetar `SessionService`
- usar `isLoggedIn()` ou `authenticated()`
- retornar `UrlTree` quando houver redirect

## Prompt recomendado para IA

```text
Recrie um service de autenticacao em Angular 19 com padrao moderno, inspirado no comportamento do auth.service deste projeto.

Use:
- Injectable providedIn root
- inject()
- nomes neutros como SessionService e AccountCredentials
- persistencia de access e refresh token
- decode do usuario a partir do JWT
- metodos login, logout, isLoggedIn, refreshToken, clearSession
- suporte a carregar contextos ativos, contextos permitidos e menu
- currentUser como signal quando fizer sentido

Evite:
- copiar nomes reais do dominio
- colocar navegacao ou token storage em componentes
- usar API legada com constructor extenso
- espalhar acesso a localStorage pelo app
```

## Checklist para a IA

- o servico usa `providedIn: 'root'`?
- a injecao usa `inject()`?
- os tokens ficam encapsulados no servico?
- existe `login()` com persistencia de token?
- existe `refreshToken()`?
- existe `clearSession()`?
- existe leitura do usuario a partir do JWT?
- os nomes sao neutros e de exemplo?

## Erros comuns que a IA deve evitar

- expor chaves de storage fora do servico
- misturar nome real e nome generico
- fazer o componente decodificar JWT
- nao limpar usuario atual no logout
- retornar tipos vagos sem necessidade
- remover suporte a refresh token
