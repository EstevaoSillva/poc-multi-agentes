# Guia de Construção de Filtros para IA

**Descrição**: Este documento define como a IA deve criar ou alterar filtros neste contexto.

A referência principal de estilo para os filtros da app é [`filters.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/filters.py), com apoio das constantes de lookup em [`../core/choices.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/choices.py).

## Regra Base Obrigatória

Os filtros de domínio desta app seguem `django_filters.rest_framework`.

O padrão de import observado é:

```python
from django.db.models import Q, OuterRef, Exists
from django_filters import rest_framework as filters, widgets

from core import choices
from manage_project import models
```

## Instrução para a IA

- filtros de domínio devem herdar de `filters.FilterSet`
- a IA deve reutilizar `core.choices` para `lookup_expr` em vez de espalhar strings arbitrárias
- a IA deve criar filtros declarativos no topo da classe
- quando a regra exigir consulta derivada, deve usar `method='nome_do_metodo'`
- quando o filtro precisar de lista, deve preferir os helpers já existentes na app, como `CharInFilter` e `NumberInFilter`

## Helpers Base da App

O arquivo atual define helpers simples para filtros do tipo `IN`:

```python
class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class NumberInFilter(filters.BaseInFilter, filters.CharFilter):
    pass
```

Regra para a IA:

- reutilizar esses helpers quando o endpoint aceitar múltiplos valores
- não reinventar um novo filtro `IN` se os existentes já resolvem

## Constantes de Lookup

O projeto centraliza os lookups em [`../core/choices.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/choices.py):

```python
FILTER_EQUALS = 'exact'
FILTER_IEQUALS = 'iexact'
FILTER_LIKE = 'unaccent__icontains'
FILTER_ISNULL = 'isnull'
FILTER_IN = 'in'
FILTER_MIN = 'gte'
FILTER_MAX = 'lte'
```

Regra para a IA:

- usar `choices.FILTER_EQUALS` para igualdade simples
- usar `choices.FILTER_LIKE` para busca textual no padrão do projeto
- usar `choices.FILTER_IN` para listas
- usar `widgets.BooleanWidget()` quando o filtro booleano vier por query string
- só usar string literal de lookup quando for um caso realmente específico e já alinhado ao restante do arquivo

## Estrutura Base para um Filter Simples

O padrão mais comum é:

```python
class ExampleFilter(filters.FilterSet):
    id = filters.NumberFilter(lookup_expr=choices.FILTER_EQUALS)
    description = filters.CharFilter(lookup_expr=choices.FILTER_LIKE)
    modified_at = filters.DateFromToRangeFilter()
    active = filters.BooleanFilter(lookup_expr=choices.FILTER_EQUALS)

    class Meta:
        model = models.Example
        fields = []
```

Esse é o formato padrão para filtros simples de listagem.

## Como Criar um Filter de Domínio

Ao criar um novo filtro em [`filters.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/filters.py), a IA deve:

- herdar de `filters.FilterSet`
- declarar explicitamente cada filtro suportado
- usar `field_name` quando o nome exposto na API não for igual ao campo do model
- usar `lookup_expr=choices.*` sempre que possível
- declarar `class Meta`
- definir `Meta.model`
- definir `Meta.fields`

## Padrão de `Meta.fields`

O arquivo usa três formatos principais:

- `fields = []`
- `fields = "__all__"`
- `fields = ['campo1', 'campo2']`

Regra para a IA:

- preferir `fields = []` quando os filtros declarados manualmente já definem o contrato da API
- usar `fields = "__all__"` apenas quando isso já for coerente com o padrão daquele recurso
- usar lista explícita quando o contrato precisa ser mais fechado

## Filtros Mais Comuns no Projeto

### Número

```python
id = filters.NumberFilter(lookup_expr=choices.FILTER_EQUALS)
project = filters.NumberFilter(field_name='project_id', lookup_expr=choices.FILTER_EQUALS)
```

### Texto

```python
description = filters.CharFilter(lookup_expr=choices.FILTER_LIKE)
responsible_name = filters.CharFilter(field_name='responsible__name', lookup_expr=choices.FILTER_LIKE)
```

### Data

```python
modified_at = filters.DateFromToRangeFilter()
start_date = filters.DateFromToRangeFilter(field_name='start_date')
```

### Booleano

```python
active = filters.BooleanFilter(
    lookup_expr=choices.FILTER_EQUALS,
    widget=widgets.BooleanWidget()
)
```

### Lista (`IN`)

```python
status_in = CharInFilter(field_name='status', lookup_expr=choices.FILTER_IN)
epic_in = NumberInFilter(field_name='epic__id', lookup_expr=choices.FILTER_IN)
```

## Padrão para `field_name`

Quando o nome do parâmetro da API não coincide com o campo do model, o projeto usa `field_name`.

Exemplos observados:

```python
risk_status = filters.NumberFilter(field_name="risk_status_id", lookup_expr=choices.FILTER_EQUALS)
responsible_name = filters.CharFilter(field_name="responsible__stakeholder__name", lookup_expr=choices.FILTER_LIKE)
doc_type = filters.CharFilter(field_name='type__name', lookup_expr=choices.FILTER_LIKE)
```

Regra para a IA:

- manter nomes de query params legíveis
- usar `field_name` para apontar ao atributo real
- não expor paths de relacionamento desnecessariamente feios como contrato público se já houver alias mais claro

## Padrão para Filtros Booleanos Especiais

O projeto usa boolean filters também para casos como:

- `isnull`
- existência de vínculo
- presença em sprint ativa
- exclusão de itens concluídos

Exemplos observados:

```python
parent_isnull = filters.filters.BooleanFilter(
    widget=widgets.BooleanWidget(),
    field_name='parent', lookup_expr='isnull'
)
```

```python
exists_in_another_sprint = filters.BooleanFilter(
    widget=widgets.BooleanWidget(),
    method='filter_exists_in_another_sprint'
)
```

Regra para a IA:

- usar `BooleanWidget()` para query params booleanos
- usar `lookup_expr='isnull'` apenas quando o caso for realmente nulidade
- usar `method=` quando houver regra derivada

## Padrão para `q`

Vários filtros da app oferecem busca ampla por `q`.

O padrão observado é:

```python
q = filters.CharFilter(method="filter_q")

def filter_q(self, queryset, name, value):
    value = (value or "").strip()
    if not value:
        return queryset

    q_obj = (
        Q(title__icontains=value) |
        Q(code__icontains=value) |
        Q(description__icontains=value)
    )

    if value.isdigit():
        q_obj |= Q(id=int(value))

    return queryset.filter(q_obj).distinct()
```

Regra para a IA:

- usar `q` quando o recurso realmente se beneficia de busca textual ampla
- sempre tratar string vazia
- usar `Q(...)` para compor campos
- chamar `.distinct()` quando a junção puder duplicar linhas

## Padrão para Filtros por Método

Quando a regra não cabe em `field_name + lookup_expr`, usar método:

```python
sprint = filters.NumberFilter(method='filter_stories_in_sprint')

def filter_stories_in_sprint(self, queryset, name, value):
    if not value:
        return queryset
    ...
```

Regra para a IA:

- nomear o método como `filter_<nome>`
- retornar `queryset` inalterado quando o valor não existir
- manter o método focado em um único critério
- usar `annotate`, `Exists`, `OuterRef` e `Q` quando isso evitar joins ruins ou consultas confusas

## Uso de `Exists` e `OuterRef`

O arquivo usa subconsultas com frequência para filtros derivados.

Casos observados:

- existência em sprint
- ausência de relacionamento
- existência em sprint ativa
- exclusão de items com execução done

Exemplo de padrão:

```python
subquery = models.SprintExecution.objects.filter(
    story=OuterRef('pk'),
    sprint_id=value
)
return queryset.annotate(
    has_sprint_execution=Exists(subquery)
).filter(has_sprint_execution=True)
```

Regra para a IA:

- preferir `Exists` quando o objetivo é saber se há vínculo, e não carregar dados
- usar `OuterRef('pk')` ou `OuterRef('id')` de forma consistente com o queryset
- manter nomes de anotações curtos e específicos

## Filtros por Relacionamento

O projeto filtra frequentemente por relações usando `__`.

Exemplos:

- `stakeholder__name`
- `responsible__stakeholder__name`
- `story_type__description`
- `type__name`
- `sprint__project`

Regra para a IA:

- usar filtros por relacionamento quando isso reflete uma necessidade real da listagem
- manter nomes públicos claros, por exemplo `responsible_name` em vez de expor diretamente `responsible__stakeholder__name`

## Convenções Observadas no Arquivo

Ao gerar um filtro novo, a IA deve respeitar estas convenções:

- classe nomeada como `NomeModelFilter`
- atributos declarativos no topo
- `q` costuma vir primeiro quando existe
- `id`, datas e `active` aparecem com frequência
- métodos auxiliares `filter_*` ficam após as declarações
- `Meta` fica no final da classe ou depois da seção declarativa principal
- para texto, o padrão predominante é `choices.FILTER_LIKE`

## Templates Úteis

### Filter simples

```python
class ExampleFilter(filters.FilterSet):
    id = filters.NumberFilter(lookup_expr=choices.FILTER_EQUALS)
    description = filters.CharFilter(lookup_expr=choices.FILTER_LIKE)
    modified_at = filters.DateFromToRangeFilter()
    active = filters.BooleanFilter(lookup_expr=choices.FILTER_EQUALS)

    class Meta:
        model = models.Example
        fields = []
```

### Filter com busca ampla

```python
class ExampleFilter(filters.FilterSet):
    q = filters.CharFilter(method='filter_q')
    id = filters.NumberFilter(lookup_expr=choices.FILTER_EQUALS)
    description = filters.CharFilter(lookup_expr=choices.FILTER_LIKE)

    def filter_q(self, queryset, name, value):
        value = (value or '').strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(description__icontains=value) | Q(code__icontains=value)
        ).distinct()

    class Meta:
        model = models.Example
        fields = []
```

### Filter com subconsulta

```python
class ExampleFilter(filters.FilterSet):
    active_relation = filters.BooleanFilter(
        widget=widgets.BooleanWidget(),
        method='filter_active_relation'
    )

    def filter_active_relation(self, queryset, name, value):
        subquery = models.RelatedModel.objects.filter(
            example=OuterRef('pk'),
            active=True
        )
        return queryset.annotate(
            has_active_relation=Exists(subquery)
        ).filter(has_active_relation=value)

    class Meta:
        model = models.Example
        fields = []
```

## Checklist para a IA

Antes de finalizar, validar:

- o filtro herda de `filters.FilterSet`
- os lookups usam `core.choices` quando aplicável
- `field_name` foi definido corretamente para relacionamentos e aliases
- `BooleanWidget()` foi usado em booleanos vindos da query string quando necessário
- filtros `IN` reutilizam `CharInFilter` ou `NumberInFilter`
- métodos `filter_*` retornam `queryset` quando não há valor
- subconsultas com `Exists` e `OuterRef` só foram usadas quando realmente necessárias
- `Meta.model` e `Meta.fields` estão corretos
- o contrato público dos parâmetros ficou coerente com os demais filtros da app

## O Que a IA Não Deve Fazer

- não criar filtros fora do padrão `FilterSet`
- não espalhar strings de lookup quando `core.choices` já resolve
- não usar `method` para algo que um `field_name + lookup_expr` resolveria
- não expor nomes de parâmetro ruins se um alias claro puder ser usado
- não esquecer `BooleanWidget()` em filtros booleanos de query string quando necessário
- não escrever filtros complexos demais sem necessidade real
- não inventar uma arquitetura diferente da observada em `filters.py`

## Prompt Recomendado

```text
Crie ou ajuste um filter seguindo exatamente o padrão do projeto.
Regras obrigatórias:
- herdar de django_filters.rest_framework.FilterSet
- usar core.choices para lookup_expr sempre que possível
- declarar filtros explicitamente no topo da classe
- usar field_name para relacionamentos e aliases de parâmetros
- usar CharInFilter e NumberInFilter para filtros IN
- usar method='filter_<nome>' quando a regra exigir lógica customizada
- usar Q, Exists e OuterRef apenas quando necessário
- definir Meta.model e Meta.fields de forma coerente com os exemplos existentes
- não inventar uma arquitetura diferente da observada em filters.py
```
