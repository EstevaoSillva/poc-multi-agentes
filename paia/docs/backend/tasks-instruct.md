# Guia de Construção de Tarefas para IA

**Descrição**: Este documento define como a IA deve criar ou alterar `tasks` assíncronas neste contexto.

A referência principal de estilo da app é [`tasks.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/manage_project/tasks.py), com apoio dos padrões já usados em [`../core/tasks.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/core/tasks.py), [`../rh/tasks.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/rh/tasks.py) e [`../levelup/tasks.py`](/mnt/c/Users/estevao.silva/PycharmProjects/bit-core/levelup/tasks.py).

## Regra Base Obrigatória

As tasks do projeto seguem Celery com `shared_task`.

O padrão dominante é:

```python
from celery import shared_task


@shared_task(bind=True, max_retries=2, queue='nome_da_fila')
def task_name(self, ...):
    try:
        ...
    except Exception as ex:
        self.retry(exc=ex, countdown=2 ** self.request.retries)
```

## Instrução para a IA

- tasks da app devem usar `@shared_task`
- a task deve declarar `queue=...` explicitamente
- usar `bind=True` quando precisar de retry, acesso a `self.request` ou metadata da task
- delegar a regra principal para `actions`, `behaviors` ou helpers quando possível
- manter a task como orquestradora de processamento assíncrono, não como local de toda a regra de domínio

## Quando Criar uma Task

No projeto atual, tasks são usadas para:

- processamento de arquivo
- envio de notificação
- rotinas agendadas
- workflows demorados
- integração com IA
- jobs que precisam retry

Regra para a IA:

- use task quando o fluxo for assíncrono, pesado, agendado ou dependente de fila
- não use task para lógica simples e imediata de request-response

## Estrutura Base

### Task simples com delegação

```python
@shared_task(bind=True, max_retries=2, queue='default')
def task_example(self, item_id: int):
    try:
        behavior = behaviors.ExampleBehavior(item_id=item_id)
        behavior.run()
    except Exception as ex:
        self.retry(exc=ex, countdown=2 ** self.request.retries)
```

### Task sem retry

```python
@shared_task(queue='some_queue')
def task_example():
    actions.ExampleActions.run()
```

Use sem `bind=True` apenas quando não houver necessidade de retry nem de contexto da task.

## Filas (`queue`)

O projeto define filas específicas por tipo de trabalho.

Exemplos observados:

- `import_worksheet`
- `default`
- `telegram`
- `email`
- `alert_curriculum`
- `alert_pending_mapping`
- `alert_anniversary`
- `expiration_date_vacancy`
- `try_contact_again`

Regra para a IA:

- sempre declarar a fila explicitamente
- escolher uma fila coerente com a natureza do job
- não deixar a fila implícita

## Retries

O padrão mais comum do projeto é:

```python
@shared_task(bind=True, max_retries=2, queue='...')
```

E no `except`:

```python
self.retry(exc=ex, countdown=2 ** self.request.retries)
```

Regra para a IA:

- usar retry exponencial simples quando o erro for transitório ou o padrão da app já indicar isso
- só usar `max_retries` diferente quando houver motivo claro
- não engolir exceções silenciosamente

## Padrão de Delegação

As tasks do projeto quase sempre delegam o trabalho real.

Destinos comuns:

- `actions.*`
- `behaviors.*`
- `helpers.*`
- funções especializadas de extração/processamento

Exemplos observados:

- `behaviors.MappingBehavior(...).run()`
- `actions.VacancyActions.expiration_date_vacancy()`
- `extract_text_from_file(...)`

Regra para a IA:

- a task deve coordenar o job
- a regra complexa deve ficar fora da task sempre que possível

## Tasks de Processamento de Arquivo

Há um padrão claro para jobs que processam arquivo salvo no model:

1. buscar a entidade pelo id
2. acessar `FileField`
3. copiar o arquivo para `/tmp/<file_name>`
4. reabrir o arquivo local
5. processar o conteúdo
6. atualizar progresso/status

Exemplo de padrão:

```python
obj = models.Content.objects.get(pk=content_id)
file_field = obj.content

file_path = f"/tmp/{file_name}"
with file_field.open("rb") as f:
    with open(file_path, "wb") as out_file:
        out_file.write(f.read())

with open(file_path, "rb") as f:
    extract_text_from_file(f)
```

Regra para a IA:

- use `/tmp` para arquivo temporário quando seguir o padrão já existente
- prefira ler do `FileField` e materializar localmente antes de passar para bibliotecas externas
- mantenha o fluxo simples e explícito

## Progress Tracking e Comunicação em Tempo Real

Tasks longas da app e do projeto usam:

- `EventProgress`
- `helpers.send_channel_message(...)` ou `send_channel_message(...)`
- payload com `percentage`, `status`, `message`

Exemplo observado:

```python
helpers.send_channel_message(
    group_name="event-progress-process-document",
    content={
        "content_id": content_id,
        "file_name": file_name,
        "percentage": 0,
        "status": "processing",
    },
)
```

Regra para a IA:

- para jobs longos, enviar progresso no início, durante etapas relevantes e no final
- usar nomes de grupo consistentes com a feature
- retornar status final claro, como `success`, `error`, `blocked`, `awaiting_confirmation`

## Uso de `EventProgress`

O padrão observado em jobs longos é:

```python
event_progress = EventProgress.objects.create(
    description=messages.SOME_MESSAGE.format(...),
    type=EventProgress.SOME_TYPE,
)
```

Ao final:

```python
event_progress.ended_at = now()
event_progress.save()
```

Regra para a IA:

- criar `EventProgress` quando o job precisa rastreabilidade operacional
- encerrar o progresso tanto em sucesso quanto em erro tratado

## Tratamento de Erros

Há dois padrões observados:

### Erro com retry

```python
except Exception as ex:
    self.retry(exc=ex, countdown=2 ** self.request.retries)
```

### Erro bloqueante sem retry completo

Em alguns casos específicos, o job:

- envia status `blocked`
- encerra `EventProgress`
- retorna sem retry

Regra para a IA:

- distinguir erro transitório de erro funcional definitivo
- se o job deve reprocessar, use retry
- se o erro deve apenas marcar bloqueio, finalize o progresso e retorne
- quando houver canal/websocket, envie a falha de forma explícita

## Localização e Contexto

O projeto mostra dois cuidados relevantes:

- tasks de notificação podem ativar idioma antes de executar
- tasks longas podem depender de variáveis de ambiente

Exemplos observados:

- `translation.activate(language)`
- `monthly_limit_tokens = int(os.getenv("MONTHLY_LIMIT_TOKENS"))`

Regra para a IA:

- preparar contexto antes da execução quando isso impactar o resultado
- limpar contexto no `finally` quando necessário, como em tradução

## Tipo de Retorno

No projeto, muitas tasks não retornam nada relevante para o chamador.

Há exceções que retornam:

- `Response(...)`
- dict simples

Regra para a IA:

- não inventar retorno complexo se ninguém consome isso
- prefira retorno simples ou nenhum retorno quando a finalidade é side-effect assíncrono

## Convenções Observadas no Arquivo

Ao gerar uma task nova, a IA deve respeitar estas convenções:

- nome de função descritivo, frequentemente com prefixo `task_` em processamento assíncrono
- decorator `@shared_task(...)` logo acima
- imports curtos e diretos
- `try/except` claro
- retry exponencial simples
- integração com `messages`, `helpers`, `actions`, `behaviors` e `EventProgress` quando fizer sentido

## Templates Úteis

### Task com retry

```python
@shared_task(bind=True, max_retries=2, queue='default')
def task_example(self, item_id: int):
    try:
        behaviors.ExampleBehavior(item_id=item_id).run()
    except Exception as ex:
        self.retry(exc=ex, countdown=2 ** self.request.retries)
```

### Task de arquivo com progresso

```python
@shared_task(bind=True, max_retries=2, queue='import_worksheet')
def task_process_example(self, obj_id: int, file_name: str):
    event_progress = EventProgress.objects.create(
        description=messages.PROCESS_FILE.format(file_name=file_name),
        type=EventProgress.PROCESS_FILE,
    )

    helpers.send_channel_message(
        group_name='event-progress-example',
        content={'percentage': 0, 'status': 'processing'}
    )

    try:
        obj = models.Example.objects.get(pk=obj_id)
        file_path = f'/tmp/{file_name}'
        ...

        helpers.send_channel_message(
            group_name='event-progress-example',
            content={'percentage': 100, 'status': 'success'}
        )
    except Exception as ex:
        helpers.send_channel_message(
            group_name='event-progress-example',
            content={'percentage': 100, 'status': 'error', 'message': str(ex)}
        )
        event_progress.ended_at = now()
        event_progress.save()
        raise self.retry(exc=ex, countdown=2 ** self.request.retries)

    event_progress.ended_at = now()
    event_progress.save()
```

### Task agendada simples

```python
@shared_task(queue='some_queue')
def task_scheduled_example():
    actions.ExampleActions.run()
```

## Checklist para a IA

Antes de finalizar, validar:

- a task realmente precisa ser assíncrona
- `@shared_task` foi usado corretamente
- a fila `queue` foi definida explicitamente
- `bind=True` foi usado quando há retry
- `max_retries` está coerente com o padrão do projeto
- a lógica principal foi delegada quando possível
- arquivos temporários usam fluxo compatível com o padrão da app
- progresso foi reportado se o job for longo
- `EventProgress` foi criado e encerrado quando necessário
- o tratamento de erro diferencia retry de bloqueio definitivo

## O Que a IA Não Deve Fazer

- não criar task para fluxo síncrono trivial
- não deixar a fila implícita
- não concentrar toda a regra de domínio dentro da task
- não ignorar erro silenciosamente
- não esquecer de encerrar `EventProgress`
- não fazer upload/processamento pesado na request se o projeto já usa task para isso
- não inventar uma arquitetura diferente da observada em `tasks.py`

## Prompt Recomendado

```text
Crie ou ajuste uma task seguindo exatamente o padrão do projeto.
Regras obrigatórias:
- usar celery.shared_task
- definir queue explicitamente
- usar bind=True e retry exponencial quando houver reprocessamento
- delegar regra complexa para actions, behaviors ou helpers
- para processamento de arquivo, seguir o padrão de materializar em /tmp antes de processar
- para jobs longos, usar EventProgress e send_channel_message quando fizer sentido
- tratar erro com retry ou bloqueio explícito, conforme o caso
- não inventar uma arquitetura diferente da observada em tasks.py
```
