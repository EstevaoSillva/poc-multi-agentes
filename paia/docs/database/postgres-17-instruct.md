# PostgreSQL 17 Instruct

**Descrição**: Este documento define o padrão obrigatório para uso de PostgreSQL 17 nos projetos do PAIA, cobrindo engine, conexão e critérios mínimos de operação. A referência operacional principal das variáveis de ambiente do backend está em [conf-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/conf-instruct.md).

## 1. Banco padrão

- Todo backend do PAIA deve considerar PostgreSQL 17 como banco relacional padrão.
- SQLite só pode ser usado para protótipo descartável ou teste isolado, nunca como configuração principal de projeto.
- O backend deve ser preparado para subir em ambiente local, homologação e produção sem troca de engine, apenas com variáveis de ambiente.

## 2. Variáveis obrigatórias no Django

Use no `settings.py` a convenção principal definida em [conf-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/conf-instruct.md):

```env
DB_ENGINE=django.db.backends.postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=paia
DB_USER=postgres
DB_PASS=123456
```

Se o projeto precisar manter aliases como `POSTGRES_*` por compatibilidade operacional ou por exigência de imagens Docker, eles devem ser tratados apenas como compatibilidade, sem substituir `DB_*` como convenção principal.

## 3. Configuração esperada no `settings.py`

O `DATABASES["default"]` deve seguir este formato:

```python
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", "paia"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASS", "123456"),
        "HOST": os.getenv("DB_HOST", "postgres"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
```

## 4. Diretrizes de operação

- Migrations fazem parte do contrato do backend e devem ser versionadas.
- O ambiente deve executar `python manage.py migrate` antes de aceitar tráfego real.
- O banco local deve usar encoding UTF-8.
- Use timezone alinhado ao projeto e mantenha `USE_TZ = True`.
- O usuário do banco deve ter permissão para criar schema, tabelas, índices e constraints do projeto.

## 5. Diretrizes de modelagem

- As regras de nomenclatura e DDL continuam centralizadas em [rules.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/database/rules.md).
- Este arquivo complementa `rules.md` com foco em engine, conexão e operação do PostgreSQL 17.
- A definição operacional das variáveis e dos aliases de infraestrutura continua centralizada em [conf-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/conf-instruct.md).

## 6. Resultado esperado

Quando um backend seguir este instruct:

- a aplicação não depende de SQLite para funcionar;
- a troca entre ambientes acontece por variável de ambiente;
- a stack fica aderente ao padrão oficial do PAIA para banco relacional.
