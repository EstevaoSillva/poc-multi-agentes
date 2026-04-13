# Guia de Construção do Service Base

**Descrição**: Este documento orienta a IA a recriar ou evoluir a base de serviços HTTP do frontend de forma moderna, tipada e reaproveitável.

## Objetivo

Este guia descreve como uma IA deve recriar o comportamento de [`src/app/services/base.service.ts`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/services/base.service.ts) usando abordagem moderna, tipada e reaproveitavel.

O servico atual e uma base generica para CRUD, rotas auxiliares, download de arquivos, `OPTIONS`, escolhas dinamicas e conexoes websocket. A IA deve preservar essa capacidade, mas com design mais claro e nomes de exemplo.

## Papel real do servico

O `BaseService<T>` atual faz:

- composicao de URL base e endpoint
- acumulacao de `HttpParams`
- configuracao de header especial de loading
- CRUD padrao
- chamadas em rotas de detalhe e de lista
- leitura paginada
- leitura de choices via `OPTIONS`
- download de arquivos
- conexao websocket
- utilitarios de parametros

## Como a IA deve reinterpretar isso

A IA deve gerar uma base generica moderna, por exemplo `ResourceService<TEntity>`, que continue permitindo:

- acesso padrao a um recurso REST
- extensao simples para recursos concretos
- operacoes auxiliares em endpoints aninhados
- centralizacao de opcoes HTTP
- suporte a arquivos e websocket quando o projeto precisar

## Nomes de exemplo obrigatorios

Usar nomes como:

- `ResourceService<TEntity>`
- `PagedResponse<TEntity>`
- `RequestLoadingMode`
- `ResourceQueryBuilder`
- `DocumentFile`
- `SocketEventPayload`

Nao usar nomes reais do dominio do projeto.

## Contrato funcional que a IA deve preservar

- existir endpoint base composto por `baseUrl + path`
- existir suporte a parametros acumulados ou composicao de query
- existir leitura de lista simples
- existir leitura paginada
- existir leitura por id
- existir create, patch, put e delete
- existir chamadas auxiliares em list route e detail route
- existir leitura de metadados via `OPTIONS`
- existir leitura de choices por campo
- existir download de blob
- existir helper para websocket quando a arquitetura usar socket

## Melhorias modernas esperadas

- `@Injectable()` apenas nas implementacoes concretas, nao necessariamente na classe base abstrata
- reduzir estado mutavel compartilhado entre chamadas
- preferir `HttpParams` imutavel por request em vez de acumular internamente quando possivel
- retornar `throwError(() => error)` em vez de `throwError(error)`
- evitar `catchError(() => from([]))` em metodos cujo retorno nao e array
- usar tipos de retorno coerentes para blob, entity e paginacao
- isolar montagem de URL em helpers privados

## Ponto critico do legado que a IA deve corrigir

O servico atual usa um estado interno mutavel de parametros e loading header. Isso e funcional, mas aumenta risco de vazamento de configuracao entre chamadas.

Na versao moderna, a IA deve preferir uma destas abordagens:

- passar `params` e `loadingMode` por metodo
- ou usar um builder descartavel que gere a chamada final

Se optar por manter API fluente, ela deve produzir uma nova instancia de configuracao por request, nao mutar estado global silenciosamente.

## Estrutura moderna recomendada

### Opcao preferida

- classe base abstrata `ResourceService<TEntity>`
- cada metodo recebe um objeto `request` opcional com `params`, `headers`, `responseType` e `loadingMode`
- servicos concretos herdam da base e definem `resourcePath`

### Opcao aceitavel

- classe helper `ResourceClient<TEntity>` criada por factory
- servicos concretos recebem essa factory e configuram endpoint

## Exemplo de tipos base

```ts
export interface PagedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

export type RequestLoadingMode = 'none' | 'slow';

export interface ResourceRequestOptions {
    params?: HttpParams;
    headers?: HttpHeaders;
    responseType?: 'json' | 'blob';
    loadingMode?: RequestLoadingMode;
}
```

## Exemplo moderno de classe base

```ts
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export abstract class ResourceService<TEntity> {
    protected readonly http = inject(HttpClient);
    protected readonly apiBaseUrl = '/api';

    protected abstract readonly resourcePath: string;

    protected resourceUrl(path = ''): string {
        return `${this.apiBaseUrl}${this.resourcePath}${path}`;
    }

    list(options?: ResourceRequestOptions): Observable<TEntity[]> {
        return this.http.get<TEntity[]>(this.resourceUrl(), this.httpOptions(options));
    }

    paged(options?: ResourceRequestOptions): Observable<PagedResponse<TEntity>> {
        return this.http.get<PagedResponse<TEntity>>(this.resourceUrl(), this.httpOptions(options));
    }

    byId(id: number | string, options?: ResourceRequestOptions): Observable<TEntity> {
        return this.http.get<TEntity>(this.resourceUrl(`${id}/`), this.httpOptions(options));
    }

    create(payload: Partial<TEntity>, options?: ResourceRequestOptions): Observable<TEntity> {
        return this.http.post<TEntity>(this.resourceUrl(), payload, this.httpOptions(options));
    }

    patch(id: number | string, payload: Partial<TEntity>, options?: ResourceRequestOptions): Observable<TEntity> {
        return this.http.patch<TEntity>(this.resourceUrl(`${id}/`), payload, this.httpOptions(options));
    }

    replace(id: number | string, payload: TEntity, options?: ResourceRequestOptions): Observable<TEntity> {
        return this.http.put<TEntity>(this.resourceUrl(`${id}/`), payload, this.httpOptions(options));
    }

    remove(id: number | string, options?: ResourceRequestOptions): Observable<void> {
        return this.http.delete<void>(this.resourceUrl(`${id}/`), this.httpOptions(options));
    }

    listRoute<TResult>(route: string, options?: ResourceRequestOptions): Observable<TResult> {
        return this.http.get<TResult>(this.resourceUrl(`${route}/`), this.httpOptions(options));
    }

    detailRoute<TResult>(id: number | string, route: string, options?: ResourceRequestOptions): Observable<TResult> {
        return this.http.get<TResult>(this.resourceUrl(`${id}/${route}/`), this.httpOptions(options));
    }

    postListRoute<TPayload, TResult>(
        route: string,
        payload: TPayload,
        options?: ResourceRequestOptions
    ): Observable<TResult> {
        return this.http.post<TResult>(this.resourceUrl(`${route}/`), payload, this.httpOptions(options));
    }

    patchDetailRoute<TPayload, TResult>(
        id: number | string,
        route: string,
        payload: TPayload,
        options?: ResourceRequestOptions
    ): Observable<TResult> {
        return this.http.patch<TResult>(this.resourceUrl(`${id}/${route}/`), payload, this.httpOptions(options));
    }

    optionsMeta(options?: ResourceRequestOptions): Observable<Record<string, unknown>> {
        return this.http.options<Record<string, unknown>>(this.resourceUrl(), this.httpOptions(options));
    }

    fieldChoices(field: string, options?: ResourceRequestOptions): Observable<unknown[]> {
        return this.optionsMeta(options).pipe(
            map((response) => ((response['actions'] as any)?.POST?.[field]?.choices as unknown[]) ?? [])
        );
    }

    downloadListRoute(route: string, options?: ResourceRequestOptions): Observable<Blob> {
        return this.http.get(this.resourceUrl(`${route}/`), this.httpOptions({ ...options, responseType: 'blob' })) as Observable<Blob>;
    }

    protected httpOptions(options?: ResourceRequestOptions) {
        const headers = this.applyLoadingHeader(options?.headers, options?.loadingMode);

        return {
            params: options?.params,
            headers,
            responseType: options?.responseType ?? 'json',
        } as const;
    }

    private applyLoadingHeader(
        headers?: HttpHeaders,
        loadingMode: RequestLoadingMode = 'none'
    ): HttpHeaders | undefined {
        if (loadingMode !== 'slow') return headers;
        return (headers ?? new HttpHeaders()).set('X-Show-Loading', 'slow');
    }
}
```

## Exemplo de implementacao concreta

```ts
import { Injectable } from '@angular/core';

export interface ExampleRecord {
    id: number;
    name: string;
}

@Injectable({ providedIn: 'root' })
export class ExampleRecordService extends ResourceService<ExampleRecord> {
    protected readonly resourcePath = '/example-record/';
}
```

## Se a IA precisar manter API fluente

Se houver forte dependencia em chaining, a IA pode usar uma camada builder assim:

```ts
const params = new HttpParams().set('active', 'true');
service.list({ params, loadingMode: 'slow' });
```

Ou:

```ts
resourceQuery(service)
    .withParam('active', 'true')
    .withLoading('slow')
    .list();
```

Mas deve evitar um objeto singleton mutavel carregando parametros de uma chamada para outra.

## Websocket

Se a feature realmente exigir websocket, a IA deve mover isso para helper mais explicito, por exemplo:

- `connectSocket<T>(event: string, params?: HttpParams)`
- endpoint socket montado por helper
- callbacks no consumidor, nao embutidos em excesso na base

Exemplo:

```ts
import { Observable } from 'rxjs';
import { webSocket } from 'rxjs/webSocket';

connectSocket<T>(event: string, params?: HttpParams): Observable<T> {
    const query = params?.toString();
    const url = query
        ? `wss://example.test/ws/${event}/?${query}`
        : `wss://example.test/ws/${event}/`;

    return webSocket<T>(url);
}
```

## Arquivos e blobs

A IA deve distinguir claramente:

- download de arquivo por list route
- download de arquivo por detail route
- upload ou geracao de arquivo por `POST`

Nao tipar blob como entidade paginada so para reaproveitar assinatura antiga.

## O que a IA deve evitar

- `catchError(() => of([]))` para metodos que retornam objeto, blob ou entidade unica
- retornar `Observable<any>` quando o retorno pode ser tipado
- misturar websocket e REST sem helper claro
- mutar `HttpParams` compartilhado entre requests
- esconder erro importante de update ou patch

## Prompt recomendado para IA

```text
Recrie um servico base generico de recursos REST em Angular 19, inspirado no comportamento do base.service deste projeto, mas com design moderno.

Use:
- classe base tipada como ResourceService<TEntity>
- inject(HttpClient)
- metodos para list, paged, byId, create, patch, replace, remove
- suporte a list route e detail route
- suporte a options metadata e field choices
- suporte a download de blob
- nomes neutros e exemplos genericos

Melhore:
- evitar estado mutavel compartilhado de params
- tipar corretamente retornos
- nao usar catchError que devolve array em qualquer erro

Evite:
- copiar a API antiga literalmente
- usar nomes reais do projeto
- manter bugs de tipagem do legado
```

## Checklist para a IA

- a base e generica e tipada?
- a URL do recurso fica centralizada?
- existe suporte a params por request?
- list e paged tem assinaturas distintas?
- blob retorna `Observable<Blob>`?
- `OPTIONS` e `choices` estao cobertos?
- websocket ficou separado de forma clara?
- o design evita estado mutavel global por request?

## Erros comuns que a IA deve evitar

- devolver array vazio para qualquer tipo de erro e qualquer tipo de retorno
- usar `any` em tudo
- acoplar demais o base service ao dominio
- manter estado fluente compartilhado entre chamadas concorrentes
- montar URLs inconsistentes com ou sem barra final
