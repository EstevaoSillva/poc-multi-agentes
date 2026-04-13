# Guia de Construção de Conjuntos de Views para IA

**Descrição**: Este documento define como a IA deve criar ou alterar `viewsets` neste contexto.

A referência principal de estilo para os endpoints da app é [`viewsets.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/viewsets.py), mas a base obrigatória dos viewsets de domínio está em [`../core/viewsets.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/viewsets.py).

## Regra Base Obrigatória

Antes de criar qualquer viewset de domínio, a IA deve garantir que a app `core` possua a classe `ViewSetBase` em [`../core/viewsets.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/viewsets.py), servindo como base dos viewsets da app.

O padrão observado é este:

```python
class ViewSetBase(viewsets.AuthViewSetBase,
                  mixins.ExpandViewSetMixin,
                  mixins.ViewSetExportMixin,
                  mixins.HistoryViewSetMixin,
                  mixins.FileAttachmentMixin):

    def get_queryset(self):
        qs = super().get_queryset()
        return self.make_queryset_expandable(self.request, qs)

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        return self.make_queryset_expandable(self.request, qs)

    def create(self, request, *args, **kwargs):
        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(request.user)
            reversion.set_comment("CREATE")
            return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        with transaction.atomic(), reversion.create_revision():
            reversion.set_user(request.user)
            reversion.set_comment("UPDATE")
            return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            return super(ViewSetBase, self).destroy(request, *args, **kwargs)
        except IntegrityError:
            raise exceptions.ForeignKeyException
```

## Instrução para a IA

- se `core/viewsets.py` não existir, a IA deve criá-lo
- se `ViewSetBase` não existir, a IA deve adicioná-lo
- se a base existir com estrutura diferente, a IA só deve alinhá-la quando a tarefa pedir ajuste da base
- todo viewset de domínio deve herdar de `core_viewsets.ViewSetBase`
- a IA não deve criar viewset de domínio herdando direto de `ModelViewSet`, `GenericViewSet` ou similares, salvo quando houver exceção explícita do projeto
- endpoints de login, registro, `me`, alteração de senha e reset de senha devem ficar em `accounts/viewsets.py`

## Estrutura Base para um ViewSet Simples

O padrão mais comum no arquivo é declarativo:

```python
class ExampleViewSet(core_viewsets.ViewSetBase):
    queryset = models.Example.objects.all()
    serializer_class = serializers.ExampleSerializer
    filterset_class = filters.ExampleFilter
    ordering = ('-id',)
    ordering_fields = '__all__'
```

Esse é o formato padrão para recursos CRUD sem comportamento especial.

## Como Criar um ViewSet de Domínio

Ao criar um novo viewset em [`viewsets.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/viewsets.py), a IA deve:

- herdar de `core_viewsets.ViewSetBase`
- declarar `queryset`
- declarar `serializer_class`
- declarar `filterset_class` quando houver filtro correspondente
- declarar `ordering`
- declarar `ordering_fields = '__all__'` quando o padrão do recurso seguir os demais endpoints da app
- usar mixins adicionais apenas quando o comportamento exigir
- delegar regra de negócio complexa para `actions`, `behaviors`, `managers` ou mixins, em vez de concentrar tudo no viewset

## Mixins Observados no Projeto

Os viewsets desta app combinam a base com mixins específicos quando necessário.

Padrões existentes:

- `mixins.ReorderViewSetMixin`
- `manage_project.mixins.LaneReorderViewSetMixin`
- `mp_mixins.ProgressMixin`
- `mp_mixins.SprintExecutionViewSetMixin`

Regra para a IA:

- usar mixin apenas quando o endpoint realmente precisar daquele contrato
- não adicionar mixin por antecipação
- preferir reaproveitar mixin existente em vez de duplicar lógica

## Padrão de ViewSet com Reorder

Quando a entidade tem ordenação mutável, o padrão é:

```python
class ExampleViewSet(core_viewsets.ViewSetBase, mixins.ReorderViewSetMixin):
    queryset = models.Example.objects.all()
    serializer_class = serializers.ExampleSerializer
    filterset_class = filters.ExampleFilter
    ordering = ('order',)
    ordering_fields = '__all__'
    reorder_serializer_class = serializers_params.ExampleReorderSerializer
```

Se houver múltiplos campos de ordenação:

```python
reorder_allowed_fields = ('order', 'lane_order')
```

Se o escopo de reordenação não for global, o viewset deve sobrescrever:

- `get_reorder_queryset_for_item`
- `get_reorder_queryset_for_create`
- `get_reorder_order_field`

Sempre respeitando o contrato já implementado em [`../core/mixins.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/mixins.py).

## Padrão de ViewSet com `@action`

A app usa `@action` para expor operações de domínio específicas, como:

- iniciar
- finalizar
- cancelar
- reordenar
- associar entidades
- retornar agregados ou contagens
- montar visão especializada, como board

Exemplo de padrão simples:

```python
@action(detail=True, methods=['PATCH'])
def finish_item(self, request, *args, **kwargs):
    response = super().partial_update(request, *args, **kwargs)
    actions.ItemActions.finish_item(item=self.get_object())
    return response
```

Exemplo de ação sem persistência padrão:

```python
@action(detail=True, methods=['PATCH'])
def cancel_item(self, request, pk=None, *args, **kwargs):
    actions.ItemActions.cancel_item(item_id=pk)
    return Response(status=status.HTTP_204_NO_CONTENT)
```

## Regras para `@action`

Ao criar uma action, a IA deve:

- usar `@action` com `detail=True` ou `detail=False` conforme o escopo
- declarar `methods=[...]` explicitamente
- usar `url_path` apenas quando necessário
- validar entrada com serializer de parâmetros quando a ação recebe payload específico
- retornar `Response(...)` com status coerente
- envolver em `@transaction.atomic` quando houver escrita múltipla ou regra crítica
- delegar a regra de negócio principal para `actions` ou `behaviors` quando o fluxo for complexo

## Validação de Parâmetros

O padrão do projeto evita validação manual extensa no corpo do viewset.

Preferência observada:

- usar `serializers_params.*Serializer` para validar `request.data` ou `request.query_params`
- chamar `is_valid(raise_exception=True)`
- ler dados de `validated_data`

Exemplo:

```python
result_serializer = serializers_params.FinishSprintSerializer(data=request.query_params)
result_serializer.is_valid(raise_exception=True)
force = result_serializer.validated_data.get('force')
```

## Padrão para `get_queryset`

Sobrescrever `get_queryset` apenas quando houver necessidade real, por exemplo:

- filtrar por parâmetros de query string
- trocar para queryset especializado do manager
- aplicar `select_related` e `prefetch_related`
- mudar o retorno para um modo compacto
- restringir o escopo por usuário ou projeto

Exemplos observados:

- filtro por `project_id` ou `risk_id`
- `with_progress()`
- `with_contents()`
- seleção otimizada para listas compactas
- montagem de queryset específico para board

Regra para a IA:

- se `super().get_queryset()` já resolve, não sobrescrever
- se houver otimização, aplicá-la de forma localizada e coerente com a action atual

## Padrão para `get_serializer_class`

O projeto usa `get_serializer_class` quando a mesma rota precisa responder com serializadores diferentes por ação ou por parâmetro.

Exemplo observado:

```python
def get_serializer_class(self):
    if self.action == 'list' and str(self.request.query_params.get('compact')).lower() == 'true':
        return serializers.StoryCompactSerializer
    return super().get_serializer_class()
```

Regra para a IA:

- só sobrescrever quando houver necessidade concreta
- manter a condição simples e legível
- retornar `super().get_serializer_class()` como fallback

## Padrão para `get_serializer_context`

Quando a serialização precisa de contexto adicional, o viewset deve:

- partir de `super().get_serializer_context()`
- adicionar apenas as chaves necessárias
- evitar lógica excessiva se isso puder ficar em service, action ou manager

No arquivo atual, o caso mais complexo é o board, com:

- cache
- agrupamento por lane
- pré-carregamento de cards
- serialização parcial para lanes faltantes

Regra para a IA:

- só repetir esse nível de complexidade quando o recurso realmente exigir uma visão agregada semelhante

## Delegação de Regra de Negócio

O padrão dominante do arquivo é não entulhar o viewset com regra de domínio.

A IA deve preferir:

- `actions.*` para ações de domínio
- `behaviors.*` para fluxos com mais etapas
- `managers.*` e querysets customizados para consulta especializada
- mixins para contratos reutilizáveis entre viewsets

O viewset deve orquestrar, não concentrar toda a regra.

## Parser e Upload

Quando o endpoint trabalha com arquivo, seguir o padrão:

```python
from rest_framework.parsers import MultiPartParser, FormParser

class ExampleAttachmentViewSet(core_viewsets.ViewSetBase):
    queryset = models.ExampleAttachment.objects.all()
    serializer_class = serializers.ExampleAttachmentSerializer
    filterset_class = filters.ExampleAttachmentFilter
    ordering_fields = '__all__'
    ordering = ('-id',)
    parser_classes = [MultiPartParser, FormParser]
```

Só adicionar `parser_classes` quando houver upload multipart real.

## Convenções Observadas no Arquivo

Ao gerar um viewset novo, a IA deve respeitar estas convenções:

- imports agrupados por origem
- classes nomeadas como `NomeModelViewSet`
- atributos declarativos no topo da classe
- métodos auxiliares privados com prefixo `_`
- actions depois da configuração principal
- uso de `status.HTTP_*` nas respostas explícitas
- uso de `request.query_params` e `request.data` conforme o caso
- uso de `super()` para preservar comportamento da base

## Templates Úteis

### ViewSet CRUD simples

```python
class ExampleViewSet(core_viewsets.ViewSetBase):
    queryset = models.Example.objects.all()
    serializer_class = serializers.ExampleSerializer
    filterset_class = filters.ExampleFilter
    ordering = ('-id',)
    ordering_fields = '__all__'
```

### ViewSet com action de domínio

```python
class ExampleViewSet(core_viewsets.ViewSetBase):
    queryset = models.Example.objects.all()
    serializer_class = serializers.ExampleSerializer
    filterset_class = filters.ExampleFilter
    ordering = ('-id',)
    ordering_fields = '__all__'

    @transaction.atomic
    @action(detail=True, methods=['PATCH'])
    def finish_example(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        actions.ExampleActions.finish_example(item=self.get_object())
        return response
```

### ViewSet com reorder

```python
class ExampleViewSet(core_viewsets.ViewSetBase, mixins.ReorderViewSetMixin):
    queryset = models.Example.objects.all()
    serializer_class = serializers.ExampleSerializer
    filterset_class = filters.ExampleFilter
    ordering = ('order',)
    ordering_fields = '__all__'
    reorder_serializer_class = serializers_params.ExampleReorderSerializer
```

## Checklist para a IA

Antes de finalizar, validar:

- existe `core/viewsets.py` com `ViewSetBase`
- o viewset herda de `core_viewsets.ViewSetBase`
- `queryset` está declarado corretamente
- `serializer_class` está correto
- `filterset_class` foi definido quando necessário
- `ordering` e `ordering_fields` seguem o padrão da app
- mixins extras foram usados apenas quando necessários
- `@action` usa método HTTP coerente
- parâmetros específicos foram validados com serializer
- regras complexas foram delegadas para `actions`, `behaviors`, `managers` ou mixins
- `super()` foi preservado quando o comportamento base precisa continuar valendo

## O Que a IA Não Deve Fazer

- não criar viewset de domínio herdando direto de `ModelViewSet`
- não duplicar regra complexa no viewset quando já cabe em `actions` ou `behaviors`
- não sobrescrever `get_queryset` sem necessidade
- não validar payload complexo manualmente se já cabe em serializer de parâmetros
- não criar action genérica demais sem semântica de domínio
- não colocar lógica de cache ou agregação pesada sem necessidade real
- não alterar o padrão declarativo da classe
- não remover o comportamento da base acidentalmente ao sobrescrever `create`, `update`, `destroy` ou filtros

## Prompt Recomendado

```text
Crie ou ajuste um viewset seguindo exatamente o padrão do projeto.
Regras obrigatórias:
- garantir que exista core/viewsets.py com a classe ViewSetBase
- viewsets de domínio devem herdar de core_viewsets.ViewSetBase
- declarar queryset, serializer_class, filterset_class, ordering e ordering_fields conforme o padrão existente
- usar mixins como ReorderViewSetMixin, ProgressMixin ou LaneReorderViewSetMixin apenas quando necessário
- validar parâmetros com serializers_params quando houver payload específico
- usar @action para operações de domínio específicas
- delegar regra complexa para actions, behaviors, managers ou mixins
- não inventar uma arquitetura diferente da observada em viewsets.py
```
