# Guia de Construção de Exceções para IA

**Descrição**: Este documento define como a IA deve criar ou alterar exceções neste contexto.

A referência principal de estilo é [`exceptions.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/exceptions.py), com apoio dos padrões compartilhados em [`../core/exceptions.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/exceptions.py) e das mensagens centralizadas em [`messages.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/messages.py).

## Regra Base Obrigatória

As exceções da app seguem `rest_framework.exceptions.APIException`.

O padrão dominante é:

```python
from rest_framework.exceptions import APIException
from manage_project import messages


class ExampleException(APIException):
    status_code = 400
    default_detail = messages.EXAMPLE_MESSAGE
```

## Instrução para a IA

- exceções de domínio da app devem herdar de `APIException`
- cada exceção deve declarar `status_code`
- cada exceção deve declarar `default_detail`
- quando a mensagem já existir em `messages.py`, a exceção deve reutilizá-la
- quando a mensagem for específica e ainda não existir, a IA deve preferir criá-la em `messages.py` antes de referenciá-la na exceção

## Estrutura Base

O padrão mais comum é:

```python
class StoryNotFoundException(APIException):
    status_code = 404
    default_detail = messages.STORY_NOT_FOUND
```

## Como Criar uma Exception

Ao criar uma nova exceção em [`exceptions.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/exceptions.py), a IA deve:

- criar uma classe com nome semântico
- herdar de `APIException`
- definir o código HTTP apropriado
- apontar `default_detail` para constante de `messages.py` quando possível

## Padrão de Nome

Os nomes observados no arquivo seguem estes formatos:

- `StoryNotFoundException`
- `StoryAlreadyAssociateSprintException`
- `SprintAlreadyFinishException`
- `StoryHasDocumentsException`

Regra para a IA:

- usar nome que descreva a regra violada
- manter sufixo `Exception`
- alinhar o nome ao vocabulário real do domínio

## Escolha de `status_code`

Os códigos observados na app são:

- `400` para regra de negócio inválida
- `404` para recurso ausente
- `202` em caso excepcional de processamento aceito

Exemplos:

```python
status_code = 400
status_code = 404
status_code = 202
```

Regra para a IA:

- usar `400` para violações de regra de domínio
- usar `404` quando a entidade ou configuração necessária não existir
- só usar outros códigos quando houver motivo claro e coerente com a API

## Padrão de `default_detail`

Há dois formatos observados:

### Reuso de constante em `messages.py`

```python
default_detail = messages.STORY_ALREADY_FINISHED
```

### Texto traduzível inline

```python
default_detail = _('Sprint already finished')
```

Regra para a IA:

- preferir `messages.*` para manter centralização
- usar `_('...')` inline apenas quando o caso for muito pontual ou o arquivo ainda não estiver centralizado para aquela mensagem
- se houver várias exceções ou usos compartilhando o mesmo texto, mover para `messages.py`

## Relação entre `messages.py` e `exceptions.py`

Na app atual, várias exceptions são apenas mapeamentos HTTP para mensagens já declaradas.

Exemplo:

```python
class StoryAlreadyStartedException(APIException):
    status_code = 400
    default_detail = messages.STORY_ALREADY_STARTED
```

Regra para a IA:

- primeiro decidir a mensagem de domínio
- depois decidir a exceção HTTP que a expõe
- não duplicar a mesma string em múltiplas exceções

## Quando Criar uma Exception Nova

Crie exceção nova quando:

- a regra de domínio aparece em mais de um ponto
- o chamador precisa de uma falha semântica clara
- a API deve responder com status e mensagem consistentes

Não crie exceção nova quando:

- o caso é apenas uma validação local simples já resolvida com `ValidationError`
- a falha não representa um conceito estável do domínio

## Exceptions vs ValidationError

Neste projeto, a separação prática é:

- `APIException` customizada para erros de domínio reutilizáveis
- `ValidationError` para payload inválido, parâmetros faltando ou validação pontual de endpoint/serializer

Regra para a IA:

- se o erro representa conceito de negócio recorrente, prefira exception customizada
- se o erro é apenas contrato de entrada, `ValidationError` costuma ser melhor

## Convenções Observadas no Arquivo

Ao gerar uma exception nova, a IA deve respeitar estas convenções:

- import de `APIException`
- uso de `gettext_lazy as _`
- uso de `messages` quando houver mensagem centralizada
- classe curta, sem métodos extras
- apenas `status_code` e `default_detail` na maioria dos casos

## Templates Úteis

### Exception com mensagem centralizada

```python
class ExampleAlreadyExistsException(APIException):
    status_code = 400
    default_detail = messages.EXAMPLE_ALREADY_EXISTS
```

### Exception com texto inline

```python
class ExampleNotConfiguredException(APIException):
    status_code = 404
    default_detail = _('Example is not configured')
```

## Checklist para a IA

Antes de finalizar, validar:

- a classe herda de `APIException`
- o nome da classe é semântico e termina com `Exception`
- `status_code` está correto
- `default_detail` reutiliza `messages.py` quando fizer sentido
- não há string duplicada desnecessariamente
- o caso realmente pede exception customizada, e não apenas `ValidationError`
- o padrão segue o que já existe em `exceptions.py`

## O Que a IA Não Deve Fazer

- não criar exceção customizada para qualquer validação pontual
- não duplicar a mesma mensagem em várias classes sem necessidade
- não omitir `status_code`
- não omitir `default_detail`
- não inventar uma arquitetura diferente da observada em `exceptions.py`

## Prompt Recomendado

```text
Crie ou ajuste uma exception seguindo exatamente o padrão do projeto.
Regras obrigatórias:
- herdar de rest_framework.exceptions.APIException
- definir status_code
- definir default_detail
- reutilizar mensagens de messages.py sempre que possível
- criar nova constante em messages.py quando a mensagem precisar ser compartilhada
- usar exception customizada para regra de domínio recorrente e ValidationError para validações pontuais
- não inventar uma arquitetura diferente da observada em exceptions.py
```
