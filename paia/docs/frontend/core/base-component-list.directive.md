# BaseComponentListDirective

**Descrição**: Este documento orienta a IA a criar e editar componentes de listagem baseados em `BaseComponentListDirective<T>`.

## Objetivo

Este arquivo orienta uma IA a criar e editar componentes de listagem baseados em [`BaseComponentListDirective<T>`](/mnt/c/Users/estevao.silva/WebstormProjects/flake-front/src/app/components/base-component-list.directive.ts).

A diretiva encapsula paginacao, ordenacao, filtros, exclusao, exportacao CSV, associacao, reordenacao e leitura de arquivos.

## Quando usar

Use esta base quando o componente representar uma tabela ou lista com:

- `MatPaginator`
- `MatSort`
- `MatTableDataSource`
- filtros livres ou por coluna
- busca paginada ou completa
- operacoes de delete, toggle, reorder ou export

Se a tela for de formulario, a IA deve preferir `BaseComponentDetailDirective`.

## Responsabilidades reais da classe

- Configurar paginador e ordenacao em `_createPaginator()`.
- Disparar busca inicial quando `searchOnInit` estiver ativo.
- Montar filtros vindos de `FpfFilterComponent` e `TableFilterDirective`.
- Aplicar `paramsOnInit` antes da busca.
- Executar `getPaginated()` ou `getAll()` conforme existencia do paginador.
- Atualizar `pageLength`, `dataSource.data` e `displayedColumns`.
- Expor operacoes padronizadas: `toggle`, `delete`, `csvExport`, `associate`, `reorder`, `viewFile`.

## Contrato de configuracao que a IA deve respeitar

`BaseListComponentOptions` aceita os seguintes pontos relevantes:

- `endpoint`: obrigatorio.
- `pk`: padrao `id`.
- `pageSize`: padrao `50`.
- `pageSizeOptions`: padrao `[50, 100, 150, 200]`.
- `searchOnInit`: dispara `search(true)` em `ngAfterViewInit()`.
- `searchRoute`: rota customizada para consultas.
- `associative`: recalcula estado de associacao.
- `associativeRoute`: rota usada em `associate()`.
- `crossTable`: usa `response.header` para colunas dinamicas.
- `paramsOnInit`: injeta parametros fixos na busca.

## Fluxo padrao de busca

Uma IA que editar a busca deve respeitar esta ordem:

1. Limpar parametros quando `search()` nao tiver sido sobrescrito.
2. Reiniciar pagina se `restartIndex` for `true`.
3. Ler filtro livre via `fpfFilterComponent`.
4. Ler filtros por coluna via `tableFilterDirective`.
5. Aplicar `paramsOnInit`.
6. Executar `beforeSearch()`.
7. Atualizar `dataSource`, `pageLength` e estados da tabela.

Nao altere essa ordem sem uma razao clara, porque ela controla o comportamento padrao do projeto.

## Exemplo de criacao de uma listagem

```ts
import { Component, Injector } from '@angular/core';
import { BaseComponentListDirective } from '../base-component-list.directive';

interface UserRow {
    id: number;
    username: string;
    email: string;
    active: boolean;
}

@Component({
    selector: 'app-user-list',
    templateUrl: './user-list.component.html',
})
export class UserListComponent extends BaseComponentListDirective<UserRow> {
    public override displayedColumns = ['id', 'username', 'email', 'active', 'actions'];

    constructor(public override injector: Injector) {
        super(injector, {
            endpoint: '/api/users/',
            formTitle: 'Usuarios',
            searchOnInit: true,
            pageSize: 50,
            pk: 'id',
        });
    }
}
```

## Exemplo de edicao de busca customizada

Quando a IA precisar adicionar um filtro fixo de negocio:

```ts
public override search(restartIndex = false, callback?: (event: number) => void): void {
    this.service.clearParameter();
    this.service.addParameter('status', 'active');
    super.search(restartIndex, callback);
}
```

Regras para a IA:

- Se sobrescrever `search()`, limpar parametros manualmente.
- Nao duplicar o restante da logica se `super.search(...)` resolver.
- Nao esquecer que `paramsOnInit` ainda sera aplicado pela base.

## Exemplo de acao de toggle

```ts
public changeActive(row: UserRow): void {
    row.active = !row.active;
    this.toggle(row, 'active', true);
}
```

O que a IA deve observar:

- `toggle()` espera que o valor ja tenha sido alterado no objeto.
- Em caso de erro, a base reverte o valor booleano.
- `searchAfterUpdate` deve ser `true` apenas quando a grade precisar recarregar.

## Exemplo de delete

```ts
public remove(row: UserRow, event: MouseEvent): boolean {
    return this.delete(row.id, row.username, {}, event);
}
```

Cuidados:

- Passe `event` quando houver clique em linha clicavel.
- Use `description` para melhorar o dialogo de confirmacao.
- Nao implemente um segundo dialogo de exclusao se a base ja cobre o caso.

## Exemplo de exportacao e reordenacao

```ts
public exportUsers(): void {
    this.csvExport('export', 'users.csv');
}

public onDrop(event: CdkDragDrop<string[]>): void {
    this.reorder(event);
}
```

## Exemplo de criacao de projeto com listagem

Quando a IA for gerar uma nova tela CRUD, a parte de lista deve seguir este roteiro:

1. Criar um componente `XListComponent` herdando da diretiva.
2. Definir `displayedColumns`.
3. Declarar `endpoint`, `pk` e `searchOnInit`.
4. Ligar `MatPaginator` e `MatSort` no template.
5. Chamar `search()` em filtros customizados.
6. Reusar `delete()`, `toggle()`, `csvExport()` e `reorder()` antes de criar metodos novos.

## Checklist de edicao para IA

- A tabela usa `dataSource.data` como fonte unica?
- `pageLength` esta sendo alimentado?
- A busca esta usando `searchRoute` correto?
- Filtros livres e filtros por coluna continuam funcionando?
- `delete()` e `toggle()` mantiveram mensagens padrao do projeto?
- A sobrescrita de `beforeSearch()` ou `search()` ainda retorna `Observable` compativel?

## Prompt recomendado para IA

```text
Crie ou edite uma listagem Angular herdando de BaseComponentListDirective.
Preserve o fluxo padrao do projeto:
- MatTableDataSource como fonte de dados
- pagina, ordenacao e filtros mantidos
- super.search() reaproveitado sempre que possivel
- delete, toggle, csvExport, reorder e associate reutilizados
- endpoint, pk, searchRoute e paramsOnInit configurados em options
Mostre exemplos de criacao e edicao de CRUD sem reimplementar o que a base ja faz.
```

## Erros comuns que a IA deve evitar

- Fazer requisicao HTTP direto no componente em vez de usar `this.service`.
- Esquecer de limpar parametros em `search()` sobrescrito.
- Atualizar `displayedColumns` fora do caso de `crossTable` sem necessidade.
- Duplicar paginacao no template e no componente.
- Misturar dados locais com `dataSource.data` e perder sincronizacao da tabela.
