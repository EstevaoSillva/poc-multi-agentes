# Guia de Construção de Comportamentos para IA

**Descrição**: Este documento define como a IA deve criar ou alterar `behaviors` neste contexto.

A referência principal de estilo é [`behaviors.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/behaviors.py).

## Regra Base Obrigatória

Nesta app, `behaviors` representam fluxos de domínio com múltiplos passos.

O padrão observado é:

- cada fluxo é encapsulado em uma classe
- a classe recebe dependências no `__init__`
- regras internas ficam em métodos privados ou auxiliares
- a execução pública acontece em `run()`
- efeitos colaterais são centralizados e ordenados

Estrutura típica:

```python
class ExampleBehavior:
    def __init__(self, item, user=None):
        self.item = item
        self.user = user

    def _validate_something(self):
        ...

    def _apply_changes(self):
        ...

    def run(self):
        self._validate_something()
        self._apply_changes()
        return self.item
```

## Instrução para a IA

- quando um fluxo de domínio tiver várias etapas, a IA deve preferir criar um behavior
- o behavior deve orquestrar mutações de estado, não representar consulta pura
- a API pública do behavior deve ser preferencialmente `run()`
- dependências de entrada devem ser recebidas no construtor
- validações, transições, reordenações e efeitos colaterais devem ficar organizados em métodos auxiliares

## Quando Usar Behavior

Na app atual, behaviors são usados para:

- iniciar sprint
- finalizar sprint
- reativar sprint
- mover story entre lanes
- reordenar lane
- associar story a sprint

Regra para a IA:

- use behavior quando houver múltiplas entidades envolvidas
- use behavior quando a operação alterar estado em sequência
- use behavior quando houver pré-condições de domínio relevantes
- não crie behavior para uma alteração trivial de um único campo sem regra extra

## Estrutura do Construtor

O construtor costuma receber:

- a entidade principal do fluxo
- parâmetros auxiliares
- flags de comportamento
- eventualmente `history_user`

Exemplos observados:

```python
def __init__(self, sprint: models.Sprint, force=False):
    self.sprint = sprint
    self.force = force
```

```python
def __init__(self, item, validated_data, request_data=None, history_user=None):
    self.item = item
    self.validated_data = validated_data
    self.request_data = request_data or {}
    self.history_user = history_user
```

Regra para a IA:

- inicializar explicitamente os atributos usados ao longo do fluxo
- não depender de estado implícito externo

## Padrão de Métodos Internos

Os behaviors da app se organizam por intenção.

Tipos comuns de método:

- validação de pré-condição
- resolução de alvo
- aplicação de transição
- sincronização entre entidades
- reordenação
- invalidação de cache

Exemplos de nomes observados:

- `_has_done`
- `_must_be_done`
- `_resolve_execution`
- `_resolve_target_lane`
- `_restore_pending_stories`
- `_replanning_pending_story`

Regra para a IA:

- cada método deve representar uma etapa lógica clara
- prefira nomes semânticos ligados ao domínio
- evite métodos longos demais acumulando todas as decisões

## Padrão para `run()`

O método `run()` é o ponto de entrada do fluxo.

Padrões observados:

- valida primeiro
- resolve contexto
- aplica mudanças
- persiste entidades
- agenda efeitos pós-commit quando necessário
- retorna a entidade principal ou `None`

Exemplo de ideia:

```python
def run(self):
    self._validate()
    self._prepare()
    self._apply()
    self._finalize()
    return self.item
```

Regra para a IA:

- `run()` deve ser legível como uma sequência de negócio
- não esconda a ordem do fluxo em chamadas indiretas demais

## Validações e Exceções

O arquivo usa fortemente exceções de domínio e `ValidationError`.

Exemplos observados:

- `exceptions.SprintAlreadyStarted`
- `exceptions.StoryInAnotherActiveSprintException`
- `ValidationError({'detail': _('...')})`

Regra para a IA:

- lançar exceção assim que a pré-condição falhar
- preferir exceções de domínio já existentes quando o caso já estiver modelado
- usar `ValidationError` para mensagens de contrato ou payload
- não retornar booleanos silenciosos para erros de domínio importantes

## Uso de Transação

Os behaviors operam em fluxos transacionais, mas nem sempre abrem `transaction.atomic()` internamente.

No projeto atual:

- alguns behaviors são chamados a partir de viewsets já anotados com `@transaction.atomic`
- outros usam `transaction.on_commit(...)` para invalidar cache

Regra para a IA:

- se o behavior for autocontido e fizer múltiplas escritas críticas, considere envolver o fluxo em transação
- se a transação já estiver garantida no chamador, não duplique sem necessidade
- use `transaction.on_commit(...)` para efeitos externos que devem acontecer só após persistência bem-sucedida

## Sincronização de Estado Entre Entidades

Um padrão forte do arquivo é manter consistência entre:

- `Story`
- `SprintExecution`
- `Sprint`
- `BoardLane`

Exemplos observados:

- mudar lane atualiza status da execução e da story
- finalizar sprint pode replanejar execuções e story global
- reativar sprint restaura estados anteriores

Regra para a IA:

- sempre pensar quais entidades precisam ser mantidas coerentes
- não atualizar só uma ponta da relação quando o domínio exige espelho de estado

## Padrão para Reordenação

Os behaviors de reordenação:

- resolvem o item de destino
- identificam a lane alvo
- validam restrições
- recalculam posições
- persistem em lote preservando histórico

Exemplo de padrão observado:

```python
bulk_update_preserving_history(
    changed,
    models.SprintExecution,
    ['lane_order'],
    default_user=self.history_user,
)
```

Regra para a IA:

- para reorder, prefira persistência em lote quando vários registros mudarem
- preserve histórico quando o projeto já oferece helper para isso
- normalize posição antes de salvar

## Uso de Histórico e Usuário

Alguns behaviors recebem `history_user` para preservar autoria em updates em lote.

Regra para a IA:

- passar `history_user` quando o fluxo altera múltiplos registros e isso importa para rastreabilidade
- não ignorar esse parâmetro se o helper chamado já suporta usuário default

## Uso de Cache

O arquivo atual invalida cache de board após mutações relevantes.

Padrão observado:

```python
transaction.on_commit(
    lambda: [
        cache_utils.invalidate_board_cache_for_scope(project_id=project_id, sprint_id=sprint_id)
        for project_id, sprint_id in affected_scopes
    ]
)
```

Regra para a IA:

- invalidar cache apenas quando o fluxo realmente afetar a visão cacheada
- preferir invalidação pós-commit
- agrupar escopos afetados antes de invalidar

## Padrão para Resolução de Alvos

Vários behaviors resolvem objetos “preferidos” ou “equivalentes”.

Exemplos observados:

- encontrar execução ativa preferencial
- traduzir lane equivalente em outra sprint
- escolher primeira lane leaf disponível

Regra para a IA:

- encapsular essa decisão em método específico
- tornar a lógica determinística
- prever fallback claro quando o alvo ideal não existir

## Convenções Observadas no Arquivo

Ao gerar um behavior novo, a IA deve respeitar estas convenções:

- nome da classe como `NomeDoFluxoBehavior`
- construtor explícito
- métodos auxiliares pequenos
- `run()` como ponto de entrada
- mutações organizadas em sequência clara
- uso de exceções de domínio
- comentários apenas quando a regra é sutil
- foco em coerência de estado entre entidades relacionadas

## Templates Úteis

### Behavior simples

```python
class ExampleBehavior:
    def __init__(self, item):
        self.item = item

    def _validate(self):
        if not self.item.active:
            raise ValidationError({'detail': _('Item must be active.')})

    def _apply(self):
        self.item.active = False
        self.item.save(update_fields=['active'])

    def run(self):
        self._validate()
        self._apply()
        return self.item
```

### Behavior com múltiplos passos

```python
class ExampleFlowBehavior:
    def __init__(self, item, related, history_user=None):
        self.item = item
        self.related = related
        self.history_user = history_user

    def _validate_relationship(self):
        ...

    def _resolve_target(self):
        ...

    def _apply_state_transition(self):
        ...

    def _sync_related_objects(self):
        ...

    def run(self):
        self._validate_relationship()
        self._resolve_target()
        self._apply_state_transition()
        self._sync_related_objects()
        return self.item
```

### Behavior com pós-commit

```python
class ExampleCacheBehavior:
    def __init__(self, item):
        self.item = item

    def run(self):
        self.item.save()
        transaction.on_commit(
            lambda: cache_utils.invalidate_board_cache_for_scope(
                project_id=self.item.project_id,
                sprint_id=getattr(self.item, 'sprint_id', None),
            )
        )
        return self.item
```

## Checklist para a IA

Antes de finalizar, validar:

- o fluxo realmente merece um behavior
- o construtor recebe explicitamente todas as dependências
- `run()` organiza a sequência principal do domínio
- pré-condições disparam exceções apropriadas
- as entidades relacionadas ficam em estado consistente após o fluxo
- efeitos colaterais pós-commit foram tratados corretamente
- updates em lote preservam histórico quando necessário
- o behavior não virou uma mistura de consulta, serializer e viewset
- o padrão segue o que já existe em `behaviors.py`

## O Que a IA Não Deve Fazer

- não usar behavior para consulta pura
- não esconder regras críticas em um método gigante sem divisão
- não mutar apenas parte do estado quando o domínio exige sincronização
- não disparar invalidação de cache antes do commit
- não usar `run()` sem retorno ou contrato claro quando o chamador depende do resultado
- não inventar uma arquitetura diferente da observada em `behaviors.py`

## Prompt Recomendado

```text
Crie ou ajuste um behavior seguindo exatamente o padrão do projeto.
Regras obrigatórias:
- encapsular o fluxo em uma classe NomeDoFluxoBehavior
- receber dependências no __init__
- dividir o fluxo em métodos auxiliares semânticos
- usar run() como ponto de entrada
- validar pré-condições com exceções de domínio ou ValidationError
- manter consistência entre entidades relacionadas
- usar transaction.on_commit para efeitos externos, como invalidação de cache, quando necessário
- preservar histórico em updates em lote quando o projeto já tiver helper para isso
- não inventar uma arquitetura diferente da observada em behaviors.py
```
