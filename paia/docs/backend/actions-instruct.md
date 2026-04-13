# Guia de Construção de Ações para IA

**Descrição**: Este documento define como a IA deve criar ou alterar `actions` neste contexto.

A referência principal de estilo é [`actions.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/actions.py), com apoio dos padrões compartilhados em [`../core/actions.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/actions.py).

## Regra Base Obrigatória

Nesta app, `actions` representam operações de domínio síncronas e reutilizáveis.

O padrão observado é:

- classes agrupadas por agregado ou contexto, como `DocumentActions`, `StoryActions`, `BoardLaneActions`
- métodos `@staticmethod`
- uso frequente de `@transaction.atomic`
- leitura e escrita de modelos diretamente
- eventual delegação para `tasks`
- eventual invalidação de cache via `transaction.on_commit(...)`

Estrutura típica:

```python
class ExampleActions:
    @staticmethod
    @transaction.atomic
    def do_something(instance, validated_data):
        ...
        return instance
```

## Instrução para a IA

- quando a operação for síncrona, reutilizável e orientada a domínio, a IA deve preferir `actions`
- actions devem agrupar operações por entidade ou agregado
- a API pública deve ser composta preferencialmente por métodos `@staticmethod`
- operações de escrita com mais de um passo devem usar `@transaction.atomic`
- a IA não deve transformar `actions` em camada de consulta pura; isso pertence mais a managers/querysets

## Quando Usar Action

Na app atual, actions são usadas para:

- criar ou atualizar documento
- iniciar, finalizar, cancelar ou excluir entidades
- criar story e criar vínculos derivados
- atualizar execuções de sprint
- associar stakeholders
- criar, atualizar, reordenar e excluir lanes

Regra para a IA:

- use action quando a operação for sincrona e reutilizável entre serializer, viewset, signal ou task
- use action quando o fluxo for curto ou moderado e não merecer um behavior separado
- se o fluxo ficar grande demais, com muitas etapas e muito estado intermediário, prefira behavior

## Estrutura de Classe

O padrão dominante é:

```python
class EntityActions:
    @staticmethod
    def helper(...):
        ...

    @staticmethod
    @transaction.atomic
    def main_action(...):
        ...
```

Regra para a IA:

- agrupar por domínio, não por tipo técnico
- manter helpers privados por convenção lógica, mesmo que o arquivo use `@staticmethod` públicos auxiliares
- evitar classes enormes misturando responsabilidades de agregados diferentes

## Padrão para `@staticmethod`

O arquivo usa `@staticmethod` quase exclusivamente.

Regra para a IA:

- preferir `@staticmethod` quando o método não depende de estado de instância
- não criar instância de classe de actions sem necessidade
- chamar como `StoryActions.finish_story(...)`, `BoardLaneActions.create_board_lane(...)`

## Padrão para `@transaction.atomic`

Grande parte das mutações relevantes usa:

```python
@staticmethod
@transaction.atomic
def action_name(...):
    ...
```

Regra para a IA:

- usar `@transaction.atomic` quando a ação escrever em múltiplas entidades ou tiver consistência crítica
- não usar atomic só por hábito se a operação for trivial e isolada, mas seguir o padrão dominante quando houver dúvida razoável

## Padrão de Delegação

As actions desta app podem delegar para:

- `tasks.*`
- `cache_utils.*`
- managers e querysets do model
- helpers da própria classe

Exemplos observados:

- `tasks.task_process_document.apply_async(...)`
- `models.SprintExecution.objects.preferred_for_story(...)`
- `BoardLaneActions._invalidate_board_scopes(...)`

Regra para a IA:

- action deve orquestrar a operação síncrona
- não duplicar lógica se já existir helper, queryset ou task apropriado

## Padrão para `transaction.on_commit`

Há dois usos fortes no arquivo:

- enfileirar task somente após commit
- invalidar cache somente após commit

Exemplo:

```python
def enqueue():
    ...

if queued_payloads:
    transaction.on_commit(enqueue)
```

Exemplo:

```python
transaction.on_commit(
    lambda: [
        cache_utils.invalidate_board_cache_for_scope(project_id=project_id, sprint_id=sprint_id)
        for project_id, sprint_id in affected_scopes
    ]
)
```

Regra para a IA:

- se a action cria ou altera dados que disparam processamento externo, enfileire isso no `on_commit`
- se a action afeta cache, invalide apenas após commit bem-sucedido

## Padrão para Operações com Arquivos

O projeto usa actions para persistir entidade principal e disparar task assíncrona depois.

Exemplo observado em documentos:

- criar `Document`
- criar `Content`
- acumular payloads
- enfileirar `task_process_document` no `on_commit`

Regra para a IA:

- actions podem cuidar da persistência da parte transacional
- o processamento pesado do arquivo deve ir para task
- nunca enfileirar antes de ter certeza de que o commit vai acontecer

## Padrão para Mutação de Estado

As actions da app alteram estado de forma explícita.

Exemplos observados:

- `status`
- `active`
- `version`
- `latest`
- `board_lane`
- `order`

Regra para a IA:

- atualizar campos explicitamente
- usar `save(update_fields=[...])` quando o escopo da alteração estiver claro
- usar `.update(...)` quando o update em lote fizer sentido

## Padrão para Sincronização Entre Entidades

Um padrão forte do arquivo é sincronizar múltiplas entidades relacionadas.

Exemplos observados:

- atualizar `Story` e `SprintExecution` em conjunto
- desativar epic e stories associadas
- replicar lanes para outras sprints ativas
- refletir alteração de lane em execuções e status das stories

Regra para a IA:

- sempre pensar quais entidades colaterais devem ser atualizadas
- não mutar apenas a entidade principal se o domínio exige consistência com entidades relacionadas

## Padrão de Helpers Internos

O arquivo usa helpers na própria classe para reduzir repetição.

Exemplos observados:

- `_sync_substories_to_new_sprint`
- `_apply_substory_lane_from_status`
- `_invalidate_board_scopes`
- `_build_scope_filter`
- `_assign_new_lane_order`
- `_replicate_lane_to_other_active_sprints`

Regra para a IA:

- extrair helper quando a action principal ficar longa ou tiver subetapas claras
- nomear helper pela intenção de negócio
- manter helpers curtos e focados

## Actions vs Behaviors

Neste projeto, a separação prática é:

- `actions`: operações síncronas reutilizáveis, geralmente mais curtas e diretas
- `behaviors`: fluxos mais longos, com várias etapas, estados intermediários e orquestração mais rica

Regra para a IA:

- se a lógica couber bem em um método estático transacional, use action
- se a lógica exigir estado interno, muitos passos e coordenação extensa, prefira behavior

## Uso de Exceções

As actions do projeto usam:

- exceções de domínio de `manage_project.exceptions`
- `ValidationError` do DRF

Exemplos observados:

- `exceptions.StoryAlreadyFinishedException()`
- `exceptions.StoryWithNoCompletedSubtasks`
- `ValidationError({'detail': _('Cannot delete a lane ...')})`

Regra para a IA:

- lançar exceção assim que a pré-condição falhar
- usar exceção de domínio existente quando o caso já estiver modelado
- usar `ValidationError` para violações de contrato ou mensagens de API

## Convenções Observadas no Arquivo

Ao gerar uma action nova, a IA deve respeitar estas convenções:

- nome da classe como `NomeDoAgregadoActions`
- métodos `@staticmethod`
- `@transaction.atomic` em mutações relevantes
- imports diretos de `models`, `exceptions`, `tasks`, `cache_utils`
- helpers internos na mesma classe quando isso mantiver coesão
- retorno explícito da entidade ou `None`, conforme o caso

## Templates Úteis

### Action simples transacional

```python
class ExampleActions:
    @staticmethod
    @transaction.atomic
    def cancel_example(example_id):
        example = models.Example.objects.get(id=example_id)
        example.status = models.Status.CANCELED
        example.active = False
        example.save(update_fields=['status', 'active'])
        return example
```

### Action com helper interno

```python
class ExampleActions:
    @staticmethod
    def _invalidate_scopes(scopes):
        transaction.on_commit(
            lambda: [
                cache_utils.invalidate_board_cache_for_scope(project_id=project_id, sprint_id=sprint_id)
                for project_id, sprint_id in scopes
            ]
        )

    @staticmethod
    @transaction.atomic
    def update_example(instance, validated_data):
        affected_scopes = {(instance.project_id, instance.sprint_id)}

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        ExampleActions._invalidate_scopes(affected_scopes)
        return instance
```

### Action que agenda task no commit

```python
class ExampleActions:
    @staticmethod
    @transaction.atomic
    def create_example(validated_data):
        instance = models.Example.objects.create(**validated_data)

        transaction.on_commit(
            lambda: tasks.task_process_example.apply_async(kwargs={'example_id': instance.id})
        )
        return instance
```

## Checklist para a IA

Antes de finalizar, validar:

- a operação realmente cabe em `actions`
- a classe foi agrupada por agregado ou contexto de domínio
- os métodos usam `@staticmethod`
- `@transaction.atomic` foi usado quando há múltiplas escritas
- helpers internos foram extraídos quando a action ficou longa
- updates sincronizam entidades relacionadas quando necessário
- task e cache só são disparados após commit
- exceções estão coerentes com o domínio e com a API
- o retorno do método está claro
- o padrão segue o que já existe em `actions.py`

## O Que a IA Não Deve Fazer

- não colocar consulta pesada de leitura em actions se isso cabe melhor em manager/queryset
- não usar action para workflow complexo demais que já pede behavior
- não disparar task ou invalidar cache antes do commit
- não duplicar regra já existente em helper, queryset ou behavior
- não criar métodos de instância sem necessidade
- não inventar uma arquitetura diferente da observada em `actions.py`

## Prompt Recomendado

```text
Crie ou ajuste uma action seguindo exatamente o padrão do projeto.
Regras obrigatórias:
- agrupar operações em classes NomeDoAgregadoActions
- usar métodos @staticmethod
- usar @transaction.atomic em operações com múltiplas escritas
- manter a action como operação síncrona de domínio reutilizável
- extrair helpers internos quando o método principal ficar longo
- sincronizar entidades relacionadas quando o domínio exigir
- usar transaction.on_commit para tasks assíncronas e invalidação de cache
- usar ValidationError ou exceções de domínio existentes quando necessário
- não inventar uma arquitetura diferente da observada em actions.py
```
