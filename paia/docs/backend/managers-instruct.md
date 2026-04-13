# Guia de Construção de Gerenciadores para IA

**Descrição**: Este documento define como a IA deve criar ou alterar `managers` e `querysets` neste contexto.

A referência principal de estilo é [`managers.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/managers.py).

## Regra Base Obrigatória

Nesta app, a regra predominante é:

- consultas compostas ficam em subclasses de `models.QuerySet`
- managers expõem essas consultas por meio de `get_queryset()`
- models usam `objects = managers.NomeDoManager()`

O padrão observado é:

```python
class ExampleQuerySet(models.QuerySet):
    def active_only(self):
        return self.filter(active=True)


class ExampleManager(models.Manager):
    def get_queryset(self):
        return ExampleQuerySet(self.model, using=self._db)

    def active_only(self):
        return self.get_queryset().active_only()
```

## Instrução para a IA

- quando houver lógica de consulta reutilizável, a IA deve criar primeiro um `QuerySet`
- o `Manager` deve ser fino e delegar para o `QuerySet`
- a IA não deve colocar regra de negócio mutável em managers
- managers devem encapsular leitura, agregação, anotação, escopo e seleção preferencial
- se a consulta é local e usada uma única vez, não criar manager novo sem necessidade

## Como Estruturar

O padrão mais comum no arquivo é:

1. criar `NomeQuerySet(models.QuerySet)`
2. implementar métodos encadeáveis nele
3. criar `NomeManager(models.Manager)`
4. retornar o queryset customizado em `get_queryset()`
5. expor atalhos no manager chamando `self.get_queryset().metodo()`

## Padrão para QuerySets

Os querysets desta app costumam:

- usar `annotate(...)`
- usar `Count`, `Sum`, `Coalesce`
- usar `Case`, `When`, `ExpressionWrapper`
- usar `Subquery` e `OuterRef`
- retornar queryset encadeável
- em alguns casos, retornar `.first()` para seleção preferencial

Exemplo de anotação de progresso:

```python
def with_progress(self):
    return self.annotate(
        total=Count(...),
        total_done=Count(...)
    ).annotate(
        progress=ExpressionWrapper(
            Case(
                When(total=0, then=Value(0.0)),
                default=F('total_done') * 100.0 / F('total'),
                output_field=models.FloatField(),
            ),
            output_field=models.FloatField(),
        )
    )
```

## Padrão para Managers

Os managers da app são deliberadamente curtos.

Exemplos observados:

- `with_progress()`
- `roots()`
- `preferred_for_story(...)`
- `accessible_by(user)`
- `count_by_project(project_id)`
- `latest_version_info(object_id, user)`

Regra para a IA:

- o manager deve apenas delegar para o queryset
- não duplicar a mesma consulta no manager e no queryset
- se o método não precisa de estado do manager, ele provavelmente pertence ao queryset

## Padrão de `get_queryset`

O contrato real da app é:

```python
def get_queryset(self):
    return ExampleQuerySet(self.model, using=self._db)
```

Regra para a IA:

- usar `self.model` e `self._db`
- não usar `objects.all()` dentro do próprio manager
- quando o queryset default já deve vir anotado, isso pode ser feito no `get_queryset()`

Exemplo observado:

```python
class EpicManager(models.Manager):
    def get_queryset(self):
        return EpicQuerySet(mp_models.Epic).progress_by_story().all()
```

Use esse padrão apenas quando a anotação default realmente fizer parte do contrato esperado do model.

## Tipos de Método Observados

### Escopo

Exemplos:

- `roots()`
- `accessible_by(user)`
- `by_project_or_sprint(project_id=None, sprint_id=None)`
- `active_or_planned_for_story(story)`

Use quando a consulta representa um recorte semanticamente relevante.

### Agregação

Exemplos:

- `with_progress()`
- `progress_by_story()`
- `progress_by_story_point()`
- `total_size()`
- `count_by_project(project_id)`

Use quando o queryset precisa devolver colunas calculadas ou agrupamentos.

### Seleção preferencial

Exemplo observado:

- `preferred_for_story(story, sprint=None)`

Use quando o domínio precisa escolher “o melhor registro” segundo uma prioridade explícita.

### Enriquecimento de dados

Exemplos:

- `with_contents()`
- `with_substories()`
- `with_related_stories()`

Use quando a consulta precisa trazer dados prontos para serializer ou viewset.

## Uso de Anotações

O arquivo usa fortemente:

- `Count`
- `Sum`
- `Coalesce`
- `ExpressionWrapper`
- `Case` / `When`
- `F`
- `Value`

Regra para a IA:

- manter nomes de anotações claros, como `total`, `total_done`, `progress`
- usar `Coalesce(..., Value(0))` quando a ausência de registros deve virar zero
- usar `Case(When(total=0, then=Value(0.0)))` para evitar divisão por zero

## Uso de `Subquery` e `OuterRef`

O projeto usa `Subquery` e `OuterRef` quando precisa:

- buscar último histórico por versão
- anotar nome relacionado sem join pesado
- checar vínculo preferencial

Exemplo observado:

```python
latest_per_version = (
    self.filter(id=OuterRef("id"), version=OuterRef("version"))
    .order_by("-history_date")
    .values("history_id")[:1]
)
```

Regra para a IA:

- usar `Subquery` quando a necessidade é de uma coluna derivada ou seleção do último registro
- manter a subquery pequena e determinística
- preferir nomes intermediários que expliquem a intenção

## Padrão de Acesso por Usuário

Alguns querysets encapsulam permissão ou visibilidade.

Exemplo:

```python
def accessible_by(self, user):
    if getattr(user, "is_superuser", False):
        return self
    return self.filter(...).distinct()
```

Regra para a IA:

- regras de visibilidade baseadas em relacionamento podem morar em queryset
- checar superusuário logo no início quando isso simplificar a consulta
- usar `.distinct()` quando joins puderem duplicar linhas

## Padrão de Seleção Preferencial

O projeto usa prioridades explícitas via `Case/When` quando precisa escolher uma execução mais relevante.

Exemplo de ideia:

```python
return queryset.annotate(
    _priority=Case(
        When(..., then=Value(0)),
        When(..., then=Value(1)),
        default=Value(99),
        output_field=models.IntegerField()
    )
).order_by('_priority', '-id').first()
```

Regra para a IA:

- usar isso quando a escolha precisa ser reprodutível
- documentar a ordem de prioridade pelo próprio código
- não deixar prioridade implícita em ordenações frágeis

## Convenções Observadas no Arquivo

Ao gerar um manager novo, a IA deve respeitar estas convenções:

- nomear classes como `NomeQuerySet` e `NomeManager`
- declarar primeiro os querysets, depois os managers
- manter métodos curtos e orientados a consulta
- usar nomes semânticos, não genéricos
- preferir retorno encadeável no queryset
- usar manager fino, com pouco código

## Templates Úteis

### QuerySet + Manager simples

```python
class ExampleQuerySet(models.QuerySet):
    def active_only(self):
        return self.filter(active=True)


class ExampleManager(models.Manager):
    def get_queryset(self):
        return ExampleQuerySet(self.model, using=self._db)

    def active_only(self):
        return self.get_queryset().active_only()
```

### QuerySet com anotação

```python
class ExampleQuerySet(models.QuerySet):
    def with_progress(self):
        return self.annotate(
            total=Count('items'),
            total_done=Count('items', filter=models.Q(items__done=True))
        ).annotate(
            progress=ExpressionWrapper(
                Case(
                    When(total=0, then=Value(0.0)),
                    default=F('total_done') * 100.0 / F('total'),
                    output_field=models.FloatField(),
                ),
                output_field=models.FloatField(),
            )
        )


class ExampleManager(models.Manager):
    def get_queryset(self):
        return ExampleQuerySet(self.model, using=self._db)

    def with_progress(self):
        return self.get_queryset().with_progress()
```

### QuerySet com seleção preferencial

```python
class ExampleQuerySet(models.QuerySet):
    def preferred_for_item(self, item):
        return self.filter(item=item).annotate(
            _priority=Case(
                When(active=True, then=Value(0)),
                default=Value(1),
                output_field=models.IntegerField()
            )
        ).order_by('_priority', '-id').first()
```

## Checklist para a IA

Antes de finalizar, validar:

- a lógica de consulta ficou em `QuerySet`, não no model nem no viewset
- o `Manager` delega para o `QuerySet`
- `get_queryset()` usa `self.model` e `self._db`
- métodos de anotação usam nomes claros
- `Coalesce`, `Case`, `When` e `Value` foram usados corretamente
- subqueries com `Subquery` e `OuterRef` são realmente necessárias
- a consulta retorna queryset encadeável quando isso for esperado
- `.first()` só foi usado quando a intenção é seleção de um único registro
- o manager segue o padrão já observado no arquivo

## O Que a IA Não Deve Fazer

- não colocar regra de mutação em managers
- não duplicar a mesma lógica no manager e no queryset
- não criar manager customizado se um `objects = models.Manager()` simples já basta
- não esconder efeitos colaterais em métodos de leitura
- não usar consulta complexa no viewset se ela cabe claramente em queryset/manager
- não inventar uma arquitetura diferente da observada em `managers.py`

## Prompt Recomendado

```text
Crie ou ajuste managers seguindo exatamente o padrão do projeto.
Regras obrigatórias:
- colocar consultas reutilizáveis em subclasses de models.QuerySet
- criar um Manager fino que delega para o QuerySet
- usar get_queryset() com self.model e self._db
- usar annotate, Count, Sum, Coalesce, Case, When, F e Value quando necessário
- usar Subquery e OuterRef apenas para casos realmente derivados
- manter mutações fora de managers; managers são para consulta e seleção
- não inventar uma arquitetura diferente da observada em managers.py
```
