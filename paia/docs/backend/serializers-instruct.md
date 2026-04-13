# Guia de Construção de Serializadores para IA

**Descrição**: Este documento define como a IA deve criar ou alterar `serializers` neste contexto.

A referência principal de estilo para os serializers da app é [`serializers.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/serializers.py), mas a base obrigatória está em [`../core/serializers.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/serializers.py) e, quando necessário, em [`../core/mixins.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/mixins.py).

## Regra Base Obrigatória

Antes de criar serializers de domínio, a IA deve garantir que a app `core` possua `SerializerBase` em [`../core/serializers.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/serializers.py).

O padrão observado é este:

```python
from rest_flex_fields import FlexFieldsModelSerializer


class SerializerBase(FlexFieldsModelSerializer, serializers.HyperlinkedModelSerializer):
    serializer_field_mapping = {
        ...
    }

    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)
        fields.insert(0, 'id')
        return fields
```

## Instrução para a IA

- se `core/serializers.py` não existir, a IA deve criá-lo
- se `SerializerBase` não existir, a IA deve adicioná-lo
- serializers de domínio devem herdar preferencialmente de `core_serializers.SerializerBase`
- a IA só deve usar `serializers.ModelSerializer` ou `serializers.HyperlinkedModelSerializer` diretamente quando houver motivo claro e já observado no projeto
- se o serializer precisa validar `full_clean()` e traduzir erros de constraint, a IA deve combinar `core_mixins.FullCleanModelSerializerMixin` com `core_serializers.SerializerBase`
- serializers de login, registro, `me` e senha devem ficar na app `accounts`

## Estrutura Base para um Serializer Simples

O padrão mais comum na app é:

```python
class ExampleSerializer(core_serializers.SerializerBase):
    class Meta:
        model = models.Example
        fields = '__all__'
```

Esse é o formato padrão para serializers CRUD simples.

## Como Criar um Serializer de Domínio

Ao criar um novo serializer em [`serializers.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/serializers.py), a IA deve:

- herdar de `core_serializers.SerializerBase`
- declarar `class Meta`
- definir `Meta.model`
- definir `Meta.fields`
- adicionar campos declarados manualmente apenas quando o padrão automático não for suficiente
- usar `expandable_fields` quando o serializer participa do padrão de expansão do projeto
- sobrescrever `create`, `update`, `validate`, `to_internal_value` ou métodos `get_*` apenas quando houver necessidade real

## Padrão com `FullCleanModelSerializerMixin`

Quando o model possui `full_clean`, constraints importantes ou mensagens amigáveis para `IntegrityError`, o padrão observado é:

```python
class ExampleSerializer(core_mixins.FullCleanModelSerializerMixin, core_serializers.SerializerBase):
    class Meta:
        model = models.Example
        fields = '__all__'

    integrity_error_map = {
        'example_unique_constraint': {
            'description': _('Message for duplicate data')
        }
    }
```

Regra para a IA:

- usar esse mixin quando o serializer precisar traduzir erro de constraint do banco
- não adicionar `integrity_error_map` sem constraint real correspondente
- manter o mapa alinhado com nomes de constraints existentes no model ou no banco

## Padrão de `expandable_fields`

O projeto usa `rest_flex_fields` via `SerializerBase`.

Quando o serializer precisa permitir expansão de relacionamentos, seguir este formato:

```python
expandable_fields = {
    'project': (
        'core.ProjectSerializer',
        {'fields': ['id', 'description']}
    ),
    'responsible': (
        'accounts.UserSerializer',
        {'fields': ['id', 'name', 'url']}
    )
}
```

Regras:

- usar nomes de serializer em string quando esse for o padrão local
- limitar `fields` ao necessário
- usar `'many': True` apenas quando o relacionamento for coleção
- usar `source` somente quando o nome exposto diferir do atributo real
- não expandir relacionamentos arbitrariamente sem necessidade de API
- a dependência instalada é `drf-flex-fields`, mas o import Python correto é `rest_flex_fields`
- não adicionar `drf_flex_fields` em `INSTALLED_APPS`

## Padrão para Campos Declarados Manualmente

O serializer pode declarar campos manualmente quando necessário, por exemplo:

- campos read-only calculados
- `SerializerMethodField`
- `ListField`
- `ChoiceField`
- `PrimaryKeyRelatedField`
- `HyperlinkedRelatedField`

Exemplos observados:

```python
progress = serializers.FloatField(read_only=True)
flags = serializers.ListField(
    child=serializers.CharField(max_length=16, required=False, allow_blank=True),
    required=False,
    allow_null=True
)
```

```python
sprint = serializers.HyperlinkedRelatedField(
    view_name='sprint-detail',
    queryset=models.Sprint.objects.all(),
    required=False,
    allow_null=True
)
```

Regra para a IA:

- declarar manualmente apenas o que realmente foge do mapeamento automático
- manter `read_only`, `write_only`, `required`, `allow_null` e `allow_blank` coerentes com o uso real

## Padrão para `to_internal_value`

O projeto aceita, em alguns endpoints, objetos vindos do frontend no formato `{id, url}`.

Nesses casos, o serializer normaliza a entrada antes de delegar ao serializer base:

```python
def to_internal_value(self, data):
    for field in ['project', 'epic', 'story_type']:
        if field in data and isinstance(data[field], dict):
            data[field] = data[field].get('url') or data[field].get('id')
    return super().to_internal_value(data)
```

Regra para a IA:

- usar esse padrão apenas quando a API realmente recebe objetos em vez de ids/urls simples
- limitar os campos convertidos
- sempre retornar `super().to_internal_value(data)`

## Padrão para `create` e `update`

O padrão dominante é não concentrar regra de negócio complexa no serializer.

A IA deve preferir:

- `actions.*` para criação/atualização com fluxo de domínio
- `behaviors.*` para processos mais elaborados
- `super().create()` e `super().update()` quando não houver lógica extra

Exemplos observados:

```python
def create(self, validated_data):
    return actions.DocumentActions.create_document(validated_data)
```

```python
def update(self, instance, validated_data):
    return behaviors.MoveStoryLaneBehavior(instance, validated_data).run()
```

Regra para a IA:

- usar delegação quando o fluxo mexe em mais de uma entidade ou tem regra de domínio forte
- não duplicar no serializer lógica que já cabe melhor em `actions` ou `behaviors`

## Padrão para `validate`

Quando a regra depende da combinação de campos e pertence ao contrato de entrada, o serializer pode sobrescrever `validate`.

Exemplo de uso observado:

- preencher `board_lane` automaticamente
- validar elegibilidade de uma story para sprint
- completar status baseado na lane encontrada

Regra para a IA:

- usar `validate(self, attrs)` para coerência de payload
- retornar `super().validate(attrs)` ao final quando o contrato base ainda deve ser preservado
- não transformar `validate` em service layer gigante

## Padrão para `SerializerMethodField`

O projeto usa `SerializerMethodField` para:

- montar URLs temporárias de arquivos
- resolver status derivado
- montar listas calculadas
- retornar relações serializadas sob contexto específico

Exemplo:

```python
file_url = serializers.SerializerMethodField(read_only=True)

def get_file_url(self, obj):
    if obj.file:
        return get_temp_minio_access_key(str(obj.file))
    return None
```

Regra para a IA:

- manter esses métodos pequenos e objetivos
- usar `self.context` quando o cálculo depender da request ou de dados pré-carregados
- evitar consultas pesadas repetidas quando a view já puder preparar contexto

## Serializers Específicos para Visões Compactas

O projeto não usa sempre um único serializer por model.

Padrões observados:

- serializer completo
- serializer compacto
- serializer específico para board
- serializer específico para histórico ou payload auxiliar

Exemplos:

- `StorySerializer`
- `StoryCompactSerializer`
- `BoardStorySerializer`
- `DocumentVersionSerializer`

Regra para a IA:

- criar serializer alternativo só quando a visão realmente exigir payload diferente
- não encher o serializer principal com exceções para todos os cenários

## Serializers Auxiliares e de Payload

Nem todo serializer representa model.

O arquivo também usa serializers para:

- validar payload de operação
- estruturar lista de itens
- expor dados históricos agregados

Exemplo:

```python
class FinalizeSprintItemSerializer(serializers.Serializer):
    sprint_execution_id = serializers.IntegerField()
    outcome = serializers.ChoiceField(choices=[('DONE', 'Done'), ('REPLANNING', 'Replanning')])
    final_story_status_id = serializers.IntegerField(required=False, allow_null=True)
```

Regra para a IA:

- usar `serializers.Serializer` quando não houver model por trás
- manter esses serializers curtos e orientados a contrato de entrada/saída

## Quando Usar `ModelSerializer` Direto

Embora o padrão dominante seja `core_serializers.SerializerBase`, o arquivo possui exceções pontuais:

- serializers muito específicos e locais
- serializers compactos de apoio
- serializers auxiliares sem necessidade de flex fields

Exemplos observados:

- `BoardStoryTypeSerializer`
- `BoardEpicSerializer`
- `ContentTypeSerializer`
- `DocumentVersionSerializer`

Regra para a IA:

- só fugir de `SerializerBase` quando houver ganho claro de simplicidade ou quando o caso já seguir esse padrão no arquivo

## Convenções Observadas no Arquivo

Ao gerar um serializer novo, a IA deve respeitar estas convenções:

- classes nomeadas como `NomeModelSerializer`
- `Meta` próximo do topo ou logo após os campos declarados
- `fields = '__all__'` é o padrão dominante
- `expandable_fields` fica fora de `Meta` na maioria dos casos
- lógica de domínio complexa é delegada
- métodos `get_*` são curtos
- uso consistente de `_('...')` em mensagens
- campos derivados como `progress`, `total`, `total_done` são `read_only=True`

## Templates Úteis

### Serializer simples

```python
class ExampleSerializer(core_serializers.SerializerBase):
    class Meta:
        model = models.Example
        fields = '__all__'
```

### Serializer com `FullClean`

```python
class ExampleSerializer(core_mixins.FullCleanModelSerializerMixin, core_serializers.SerializerBase):
    class Meta:
        model = models.Example
        fields = '__all__'

    integrity_error_map = {
        'example_unique_constraint': {
            'description': _('Example already exists')
        }
    }
```

### Serializer com expansão

```python
class ExampleSerializer(core_serializers.SerializerBase):
    class Meta:
        model = models.Example
        fields = '__all__'

    expandable_fields = {
        'project': (
            'core.ProjectSerializer',
            {'fields': ['id', 'description']}
        )
    }
```

### Serializer auxiliar de payload

```python
class ExampleActionSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=[('START', 'Start'), ('DONE', 'Done')])
```

## Checklist para a IA

Antes de finalizar, validar:

- existe `core/serializers.py` com `SerializerBase`
- o serializer herda de `core_serializers.SerializerBase`, salvo exceção justificada
- `Meta.model` e `Meta.fields` estão corretos
- `expandable_fields` foi usado apenas quando necessário
- campos declarados manualmente realmente precisam existir
- `read_only`, `write_only`, `required`, `allow_null` e `allow_blank` estão corretos
- `to_internal_value` foi sobrescrito apenas se a entrada exigir normalização
- `create`, `update` e `validate` não concentraram regra de domínio demais
- `FullCleanModelSerializerMixin` foi usado quando há constraints que precisam de validação amigável
- o serializer segue o padrão já observado no arquivo

## O Que a IA Não Deve Fazer

- não criar serializers de domínio fora do padrão `SerializerBase` sem motivo claro
- não duplicar regra pesada de negócio dentro do serializer
- não expandir relacionamentos sem necessidade
- não declarar manualmente campos que o serializer base já resolve
- não sobrescrever `to_internal_value`, `validate`, `create` ou `update` sem necessidade real
- não usar serializer único para resolver todos os cenários se o projeto já separa visão completa, compacta e auxiliar
- não inventar uma arquitetura diferente da observada em `serializers.py`

## Prompt Recomendado

```text
Crie ou ajuste um serializer seguindo exatamente o padrão do projeto.
Regras obrigatórias:
- garantir que exista core/serializers.py com SerializerBase
- serializers de domínio devem herdar de core_serializers.SerializerBase, salvo exceções já compatíveis com o projeto
- usar Meta.model e Meta.fields conforme o model real
- usar expandable_fields quando a API precisar expandir relacionamentos
- usar FullCleanModelSerializerMixin quando houver validação de full_clean/constraints
- validar payload em validate quando necessário
- usar to_internal_value apenas para normalizar entrada vinda do frontend
- delegar criação e atualização complexas para actions ou behaviors
- não inventar uma arquitetura diferente da observada em serializers.py
```
