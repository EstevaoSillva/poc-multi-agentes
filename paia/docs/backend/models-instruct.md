# Guia de Construção de Modelos para IA

**Descrição**: Este documento define como a IA deve criar ou alterar `models` neste contexto.

A referência principal de estilo para os models de domínio é [`models.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/models.py), mas antes de qualquer model de domínio
existir, a IA deve garantir a existência da classe base `ModelBase` na app `core`.

## Regra Base Obrigatória

Antes de criar qualquer model de domínio, 
a IA deve garantir que exista o arquivo `core/models.py` com esta implementação:

```python
from django.db import models
from django.utils.translation import gettext_lazy as _


class ModelBase(models.Model):
    id = models.BigAutoField(
        db_column='id',
        null=False,
        primary_key=True,
        verbose_name=_('Id')
    )
    created_at = models.DateTimeField(
        db_column='dt_created_at',
        auto_now_add=True,
        null=True,
        verbose_name=_('Created at')
    )
    modified_at = models.DateTimeField(
        db_column='dt_modified_at',
        auto_now=True,
        null=True,
        verbose_name=_('Modified at')
    )
    active = models.BooleanField(
        db_column='cs_active',
        null=False,
        default=True,
        verbose_name=_('Active'),
    )

    class Meta:
        abstract = True
        managed = True
        default_permissions = ('add', 'change', 'delete', 'view')
```

## Instrução para a IA

- se `core/models.py` não existir, a IA deve criá-lo
- se `ModelBase` não existir, a IA deve adicioná-lo
- se a `ModelBase` existir com estrutura diferente, a IA deve ajustá-la para este padrão quando a tarefa pedir alinhamento da base
- todo model de domínio deve herdar de `core_models.ModelBase`
- a IA não deve criar model de domínio herdando direto de `models.Model`
- autenticação, perfil e usuário devem viver na app `accounts`, não em apps de domínio
- relacionamentos com usuário devem usar `settings.AUTH_USER_MODEL`
- a IA não deve importar `django.contrib.auth.models.User` diretamente em apps de domínio

## Criação de Model de Domínio

Ao criar um novo model, a IA deve:

- seguir o estilo já existente no arquivo
- herdar de `core_models.ModelBase`
- declarar `Meta.db_table` com schema `"manage_project"`
- usar `HistoricalRecords`
- mapear colunas com `db_column` quando aplicável
- manter coerência com o projeto em:
  - `choices`
  - `constraints`
  - `indexes`
  - `related_name`
  - `on_delete`
- adicionar regras de negócio em `save`, `clean` ou métodos auxiliares apenas quando necessário e consistente com o domínio

## Estrutura Base

Use este template como ponto de partida:

```python
class ExampleModel(core_models.ModelBase):
    project = models.ForeignKey(
        to='core.Project',
        on_delete=models.DO_NOTHING,
        db_column='id_project',
        null=False
    )
    description = models.CharField(
        max_length=256,
        null=False,
        db_column='tx_description'
    )

    history = HistoricalRecords(table_name='"history"."example_model"')

    class Meta:
        db_table = '"manage_project"."example_model"'

    def __str__(self):
        return self.description
```

## Padrão Obrigatório

### 1. Herança

Todo model deve herdar de:

```python
class NomeDoModel(core_models.ModelBase):
```

Não usar `models.Model` diretamente.

### 2. Nome de tabela

Sempre declarar `Meta.db_table` no formato:

```python
db_table = '"manage_project"."nome_da_tabela"'
```

Se o model já seguir outro comportamento no arquivo, como `managed = True`, preserve esse padrão quando fizer sentido.

### 3. Histórico

Todo model deste arquivo segue o padrão de histórico:

```python
history = HistoricalRecords(table_name='"history"."nome_da_tabela"')
```

O nome da tabela de histórico deve corresponder ao nome físico da tabela principal.

### 4. Colunas físicas

Quando o projeto mapeia nomes legados do banco, a IA deve usar `db_column`.

Padrões recorrentes no arquivo:

- `id_*` para chaves estrangeiras
- `tx_*` para textos
- `dt_*` para datas
- `nb_*` para números
- `cs_*` para status ou flags legadas

Exemplos:

```python
db_column='id_project'
db_column='tx_description'
db_column='dt_start'
db_column='nb_order'
db_column='cs_status'
```

Se o campo equivalente no arquivo não usa `db_column`, a IA não deve inventar um por conta própria.

### 5. Relacionamentos

Para relacionamentos, seguir o padrão dominante:

```python
models.ForeignKey(
    to='app.Model',
    on_delete=models.DO_NOTHING,
    db_column='id_model',
    null=False
)
```

Regras:

- usar `to='app.Model'` em string quando este for o padrão local
- usar `related_name` apenas quando necessário ou quando já houver padrão equivalente
- usar `models.CASCADE` apenas quando o domínio já indicar dependência forte
- respeitar `null=True` e `blank=True` conforme comportamento esperado no banco e no formulário

### 6. Choices

Quando houver enumeração, seguir o padrão com `models.TextChoices`, preferencialmente dentro do próprio model quando o escopo for local.

Exemplo:

```python
class Type(models.TextChoices):
    OPPORTUNITY = '1', _('Opportunity')
    THREAT = '2', _('Threat')
```

Para campos com choices:

```python
type = models.CharField(
    max_length=1,
    null=False,
    db_column='tx_type',
    choices=Type.choices
)
```

### 7. `__str__`

Quase todo model deve implementar `__str__` com o atributo mais legível.

Preferências:

- `description`
- `name`
- `title`
- combinação curta de campos relevantes

### 8. Managers customizados

Se existir manager específico no domínio, seguir o padrão:

```python
objects = managers.NomeDoManager()
```

Não criar manager novo sem necessidade real.

### 9. Constraints e indexes

Quando o domínio exigir unicidade, performance de ordenação ou busca frequente, usar `constraints` e `indexes` no `Meta`, seguindo o estilo já existente.

Exemplos do projeto:

- `models.UniqueConstraint(...)`
- `unique_together`
- `models.Index(...)`
- índices condicionais com `models.Q(...)`
- unicidade com `UnaccentLower(models.F(...))`

Se houver necessidade de comparação sem acento e sem diferença entre maiúsculas e minúsculas, considerar o padrão já usado com `UnaccentLower`.

### 10. Regras de negócio

Regras de negócio podem existir em:

- `save`
- `clean`
- métodos auxiliares privados
- `delete`

Mas a IA só deve adicionar essas regras quando houver necessidade clara no domínio.

Padrões já existentes no arquivo:

- geração automática de ordem sequencial
- geração de código
- normalização de texto antes de salvar
- validação de conflito entre entidades relacionadas
- sincronização de estado entre entidades

## Convenções Observadas no Arquivo

Ao gerar código novo, a IA deve respeitar estas convenções:

- campos são declarados de forma explícita, um por bloco
- argumentos costumam ficar quebrados em várias linhas
- `history` normalmente fica após os campos
- `objects` pode ficar próximo de `history` ou logo depois
- `class Meta` vem depois dos campos e antes de métodos
- métodos auxiliares privados usam prefixo `__`
- comentários são raros e só aparecem quando explicam regra de negócio real

## Exemplo Mais Completo

```python
class ExampleItem(core_models.ModelBase):
    class Status(models.TextChoices):
        NOT_STARTED = '1', _('Not Started')
        DONE = '2', _('Done')

    project = models.ForeignKey(
        to='core.Project',
        on_delete=models.DO_NOTHING,
        db_column='id_project',
        null=False
    )
    title = models.CharField(
        max_length=256,
        null=False,
        db_column='tx_title'
    )
    status = models.CharField(
        max_length=1,
        null=False,
        db_column='cs_status',
        choices=Status.choices,
        default=Status.NOT_STARTED
    )
    order = models.SmallIntegerField(
        null=False,
        db_column='nb_order',
        default=1
    )

    history = HistoricalRecords(table_name='"history"."example_item"')

    class Meta:
        db_table = '"manage_project"."example_item"'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'title'],
                name='example_item_project_title_unique'
            ),
        ]

    def __str__(self):
        return self.title

    def __generate_order_sequence(self):
        is_create = self.pk is None
        if is_create and (self.order is None or self.order == 1):
            last = ExampleItem.objects.filter(
                project=self.project
            ).aggregate(models.Max('order')).get('order__max') or 0
            self.order = last + 1

    def save(self, *args, **kwargs):
        self.__generate_order_sequence()
        super().save(*args, **kwargs)
```

## Checklist para a IA

Antes de finalizar um model novo, validar:

- o model herda de `core_models.ModelBase`
- a tabela usa schema `"manage_project"`
- existe `HistoricalRecords`
- os `db_column` seguem o padrão do projeto
- `ForeignKey`, `OneToOneField` e `related_name` estão coerentes
- `null` e `blank` refletem o comportamento real esperado
- `choices`, `default`, `constraints` e `indexes` foram definidos quando necessário
- `__str__` foi implementado
- nenhuma convenção nova foi inventada sem existir no arquivo atual

## O Que a IA Não Deve Fazer

- não usar `models.Model` no lugar de `core_models.ModelBase`
- não omitir `Meta.db_table`
- não omitir `history`
- não trocar nomes físicos de coluna sem necessidade
- não criar campos com convenções fora do padrão do arquivo
- não usar `related_name` arbitrário
- não adicionar validações ou automações em `save` sem justificativa de domínio
- não refatorar models antigos só para "modernizar"
- não mudar o estilo do arquivo para um formato diferente do já adotado

## Prompt Recomendado para Uso com IA

Use um prompt parecido com este:

```text
Crie um novo model em models.py seguindo exatamente o padrão já existente no arquivo.
Regras obrigatórias:
- herdar de core_models.ModelBase
- usar Meta.db_table com schema "manage_project"
- usar HistoricalRecords com schema "history"
- manter db_column no padrão legado do projeto
- seguir o estilo de ForeignKey, choices, __str__, constraints e indexes já usados
- não inventar convenções novas
- só adicionar regra em save/clean se houver necessidade explícita de negócio
Antes de concluir, revise se o model ficou consistente com os exemplos existentes no arquivo.
```

## Referência Principal

O único padrão fonte para criação de novos models neste contexto é [`models.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/models.py).
