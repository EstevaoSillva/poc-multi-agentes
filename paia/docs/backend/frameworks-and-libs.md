# Frameworks e Bibliotecas do Backend

**Descrição**: Este documento define a stack base permitida para projetos backend do PAIA. Ele registra as bibliotecas preferenciais e o papel de cada uma, sem substituir os instructs especializados de models, serializers, viewsets, actions, tasks ou configuração.

## 1. Stack base

- `python 3.14`
- `django`
- `djangorestframework`
- `djangorestframework-simplejwt`
- `psycopg2-binary`
- `django-filter`
- `drf-flex-fields`
- `python-dotenv`
- `django-storages`
- `boto3`
- `celery`

## 2. Bibliotecas obrigatórias por responsabilidade

### 2.1. Backend web e API

- `django`: framework base do backend.
- `djangorestframework`: criação de APIs REST, serializers, autenticação, paginação e viewsets.
- `djangorestframework-simplejwt`: autenticação baseada em JWT para a app `accounts`.

Diretriz:

- endpoints devem seguir o padrão arquitetural documentado em [architeture-back.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/architeture-back.md);
- regras de viewsets e serializers devem seguir [viewsets-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/viewsets-instruct.md) e [serializers-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/serializers-instruct.md).
- login, registro e senha devem seguir [accounts-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/accounts-instruct.md).

### 2.2. Banco de dados

- `psycopg2-binary`: driver de conexão com PostgreSQL.

Diretriz:

- o banco relacional padrão é PostgreSQL 17;
- regras de engine e conexão ficam em [postgres-17-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/database/postgres-17-instruct.md).

### 2.3. Filtros e consultas de API

- `django-filter`: definição de filtros por query string.
- `drf-flex-fields`: expansão controlada de relações e payloads mais dinâmicos.

Diretriz operacional:

- o pacote instalado é `drf-flex-fields`;
- o import Python correto é `rest_flex_fields`;
- a biblioteca não deve ser registrada como `drf_flex_fields` em `INSTALLED_APPS`.

Exemplo com `django-filter`:

```python
import django_filters


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Product
        fields = ["price", "release_date"]
```

Diretriz:

- filtros devem seguir [filters-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/filters-instruct.md);
- serializers que usam expansão devem seguir [serializers-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/serializers-instruct.md).

### 2.4. Configuração por ambiente

- `python-dotenv`: leitura do arquivo central de configuração, como `paia.conf` ou equivalente.

Diretriz:

- variáveis de ambiente e serviços Docker devem seguir [conf-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/conf-instruct.md).

### 2.5. Storage de arquivos

- `django-storages`: integração de storage com Django.
- `boto3`: cliente S3 usado por `django-storages`.

Diretriz:

- quando houver MinIO ou S3 compatível, o projeto deve usar `AWS_*` em `settings.py`;
- a regra transversal de storage está em [architeture-back.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/architeture-back.md).

### 2.6. Assincronicidade

- `celery`: processamento assíncrono, filas e jobs longos.

Diretriz:

- tasks devem seguir [tasks-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/tasks-instruct.md).

## 3. Restrições

- não adicionar biblioteca sem necessidade real do domínio;
- não introduzir alternativa concorrente quando já existe padrão aprovado no repositório;
- não misturar múltiplas abordagens para o mesmo problema sem motivo explícito.

## 4. Resultado esperado

Quando este documento for seguido:

- a stack backend fica previsível;
- a IA gera código mais consistente;
- dependências de banco, API, filtros, storage e assíncrono seguem um padrão único do projeto.
