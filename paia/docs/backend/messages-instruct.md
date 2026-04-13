# Guia de Construção de Mensagens para IA

**Descrição**: Este documento define como a IA deve criar ou alterar mensagens neste contexto.

A referência principal de estilo é [`messages.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/messages.py), com apoio dos padrões em [`../core/messages.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/messages.py).

## Regra Base Obrigatória

As mensagens da app são centralizadas como constantes traduzíveis.

O padrão observado é:

```python
from django.utils.translation import gettext_lazy as _

EXAMPLE_MESSAGE = _('Example message')
```

## Instrução para a IA

- mensagens reutilizáveis da app devem ser declaradas em `messages.py`
- cada mensagem deve ser uma constante em maiúsculas
- a constante deve usar `gettext_lazy as _`
- textos compartilhados entre exception, serializer, task ou action devem ser centralizados aqui

## Estrutura Base

O padrão dominante é:

```python
from django.utils.translation import gettext_lazy as _

STORY_NOT_FOUND = _("story-not-found")
SPRINT_ALREADY_STARTED = _("Cannot start a sprint that has already started.")
PROCESS_DOCUMENT = _('Processing document {file_name}')
```

## Como Criar uma Message

Ao criar uma nova mensagem em [`messages.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/messages.py), a IA deve:

- declarar uma constante em maiúsculas com underscores
- usar `_("...")` ou ` _('...') `
- escolher um nome estável e semântico
- pensar se a mensagem será reutilizada por exception, task, serializer ou action

## Padrão de Nome

Os nomes observados no arquivo seguem o estilo:

- `STORY_NOT_FOUND`
- `SPRINT_ALREADY_EXIST`
- `NO_COMPLETED_SUBSTORIES`
- `PROCESS_DOCUMENT`
- `STORY_HAS_HISTORY`

Regra para a IA:

- usar nomes curtos, descritivos e estáveis
- evitar nomes excessivamente técnicos
- nomear pela semântica do erro, evento ou mensagem de negócio

## Tipos de Mensagem Observados

### Erro de domínio

Exemplos:

- `STORY_ALREADY_IS_DONE`
- `SPRINT_ALREADY_STARTED`
- `STORY_CAN_NOT_ASSOCIATED_TO_SPRINT`

### Erro de restrição/remoção

Exemplos:

- `STORY_HAS_DOCUMENTS`
- `STORY_HAS_COMMENTS`
- `STORY_HAS_SUBSTORIES`

### Mensagem operacional

Exemplo:

- `PROCESS_DOCUMENT = _('Processing document {file_name}')`

### Mensagem de validação técnica

Exemplo:

- `SPRINT_CODE = _('This unique code for the story already exists')`

## Uso de Placeholders

O arquivo já usa placeholders formatáveis:

```python
PROCESS_DOCUMENT = _('Processing document {file_name}')
```

Regra para a IA:

- usar placeholders nomeados quando a mensagem precisar interpolação
- manter os nomes de placeholder claros
- não interpolar valores diretamente dentro de `messages.py`
- fazer a interpolação no ponto de uso com `.format(...)`

## Quando Criar Mensagem Nova

Crie nova constante quando:

- o texto for reutilizado em mais de um lugar
- a mensagem representar conceito de domínio
- a app precisar padronização da resposta

Não crie nova constante quando:

- o texto é totalmente local e pontual
- o caso é uma mensagem inline única sem reutilização previsível

## Messages vs Texto Inline

No projeto atual existe mistura:

- mensagens centralizadas em `messages.py`
- textos inline com `_('...')` em alguns pontos

Regra para a IA:

- preferir `messages.py` para mensagens compartilhadas
- usar inline apenas quando a mensagem for claramente local e não reutilizável
- se um texto inline começar a aparecer em vários lugares, movê-lo para `messages.py`

## Relação com `exceptions.py`

Muitas exceptions da app consomem diretamente constantes deste arquivo.

Exemplo:

```python
class StoryHasDocumentsException(APIException):
    status_code = 400
    default_detail = messages.STORY_HAS_DOCUMENTS
```

Regra para a IA:

- ao criar exception reutilizável, avaliar primeiro se a mensagem deve entrar em `messages.py`
- evitar duplicação de literal entre `exceptions.py`, `actions.py`, `serializers.py` e `tasks.py`

## Relação com Tasks

Tasks longas da app usam mensagens operacionais centralizadas.

Exemplo:

```python
description=messages.PROCESS_DOCUMENT.format(file_name=file_name)
```

Regra para a IA:

- mensagens de progresso, processamento e status operacional também podem viver aqui quando forem parte do contrato da feature

## Convenções Observadas no Arquivo

Ao gerar uma mensagem nova, a IA deve respeitar estas convenções:

- arquivo com apenas constantes
- import único de `gettext_lazy as _`
- constantes em caixa alta
- uma mensagem por linha, salvo quebra necessária por comprimento
- texto em inglês no padrão atual da app, a menos que a feature siga outro idioma já estabelecido

## Templates Úteis

### Mensagem simples

```python
EXAMPLE_ALREADY_EXISTS = _('Example already exists')
```

### Mensagem de remoção bloqueada

```python
EXAMPLE_HAS_DEPENDENCIES = _('Cannot delete example with associated dependencies.')
```

### Mensagem com placeholder

```python
PROCESS_EXAMPLE = _('Processing example {file_name}')
```

## Checklist para a IA

Antes de finalizar, validar:

- a mensagem realmente merece centralização
- a constante está em maiúsculas com underscores
- o texto usa `gettext_lazy as _`
- o nome da constante descreve bem a intenção
- placeholders, se houver, são nomeados e estáveis
- a mensagem não duplica outra já existente
- o padrão segue o que já existe em `messages.py`

## O Que a IA Não Deve Fazer

- não criar constantes para textos puramente locais sem necessidade
- não duplicar mensagens equivalentes com nomes diferentes
- não interpolar valores diretamente no arquivo de constantes
- não misturar lógica com mensagens
- não inventar uma arquitetura diferente da observada em `messages.py`

## Prompt Recomendado

```text
Crie ou ajuste mensagens seguindo exatamente o padrão do projeto.
Regras obrigatórias:
- centralizar mensagens reutilizáveis em messages.py
- usar constantes em maiúsculas com underscores
- usar django.utils.translation.gettext_lazy as _
- usar placeholders nomeados quando houver interpolação
- reutilizar constantes já existentes sempre que possível
- mover para messages.py textos que passarem a ser compartilhados por exceptions, tasks, serializers ou actions
- não inventar uma arquitetura diferente da observada em messages.py
```
