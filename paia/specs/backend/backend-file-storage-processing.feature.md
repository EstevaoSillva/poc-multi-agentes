# Feature: Upload, storage e processamento assíncrono de arquivos

## Objetivo
Definir o padrão para features backend que recebem arquivo, armazenam em S3 compatível e disparam processamento assíncrono.

## Regras
- o storage deve usar `AWS_*`
- arquivos devem ser persistidos de forma transacional antes do processamento
- o processamento pesado deve ocorrer em `tasks.py`
- o disparo da task deve ocorrer após commit
- mensagens de progresso e erro devem ser centralizadas quando fizer sentido

## Fluxo esperado
1. receber o arquivo no endpoint
2. validar payload e contexto
3. persistir a entidade principal
4. persistir metadados ou conteúdo relacionado
5. disparar task no `transaction.on_commit(...)`
6. acompanhar status de processamento

## Arquivos esperados
- `serializers.py`
- `actions.py`
- `tasks.py`
- `messages.py`
- `exceptions.py`
- `settings.py` configurado com storage S3 compatível

## Serviços esperados
- storage compatível com S3 via MinIO ou equivalente
- fila assíncrona via Celery
- broker como Redis quando aplicável

## Referências
- `docs/backend/conf-instruct.md`
- `docs/backend/tasks-instruct.md`
- `docs/backend/actions-instruct.md`
- `docs/backend/messages-instruct.md`
- `docs/backend/exceptions-instruct.md`

## Checklist
- o arquivo é persistido antes da task?
- a task é disparada apenas após commit?
- o endpoint não concentra processamento pesado?
- mensagens de progresso e falha estão padronizadas?
