# Guia de Configuração Operacional do Backend

**Descrição**: Este documento define o padrão para centralizar variáveis de ambiente e nomes de serviços Docker do backend. Ele deve ser a fonte principal para configuração operacional de banco, cache, storage e demais dependências de infraestrutura do projeto.

## 1. Objetivo

- Todo backend do PAIA deve concentrar suas variáveis de ambiente operacionais em um arquivo de configuração único, como `paia.conf` ou `.env`.
- Esse arquivo deve cobrir banco de dados, serviços Docker auxiliares e credenciais mínimas necessárias para a aplicação subir localmente.
- A configuração deve permitir troca de ambiente sem alterar código-fonte, apenas variáveis.

## 2. Regra de centralização

- Toda variável de conexão com banco, cache, mensageria, storage ou serviço externo executado via Docker deve ficar no arquivo central de configuração.
- Não espalhe host, porta, usuário, senha ou bucket diretamente em `settings.py`, `docker-compose`, tasks ou módulos de negócio.
- O backend deve ler essas definições por `os.getenv(...)` ou mecanismo equivalente.
- Quando existir mais de um nome compatível para a mesma configuração, defina um padrão principal e trate os aliases apenas como compatibilidade.

## 3. Banco de dados

- O banco relacional padrão continua sendo PostgreSQL 17, conforme [postgres-17-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/database/postgres-17-instruct.md).
- Este documento é a referência operacional principal para variáveis de ambiente de banco no backend.
- Para compatibilidade com o projeto atual, o backend pode aceitar `DB_*` e `POSTGRES_*`, mas a convenção principal deve ser `DB_*`.
- Neste repositório, o arquivo [paia.conf](/mnt/c/Users/estevao.silva/PycharmProjects/paia/paia.conf) já expõe a convenção baseada em `DB_*`.

Exemplo mínimo:

```env
DB_ENGINE=django.db.backends.postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=paia
DB_USER=postgres
DB_PASS=123456
```

## 4. Serviços Docker

- Todo serviço de infraestrutura executado em Docker deve possuir variáveis explícitas para hostname, porta e credenciais quando aplicável.
- O hostname deve preferir o nome do serviço definido no `docker-compose`, pois ele vira o DNS interno da rede Docker.
- Se um serviço não for usado pelo projeto, suas variáveis não precisam existir.
- Se um novo serviço passar a ser obrigatório, este documento e o arquivo central de configuração devem ser atualizados no mesmo ciclo.

### 4.1. Redis

Use quando houver cache, filas, locks distribuídos, Celery broker ou backend de resultado.

```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_URL=redis://redis:6379/0
```

### 4.2. MinIO

Use quando houver storage S3 compatível para arquivos, anexos, mídia privada ou artefatos.

```env
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=paia
MINIO_USE_SSL=false
MINIO_REGION=us-east-1
```

### 4.3. Serviços adicionais

Para qualquer outro serviço obrigatório do projeto, siga o mesmo padrão:

- prefixo semântico por serviço, como `RABBITMQ_*`, `ELASTICSEARCH_*`, `SMTP_*` ou `CELERY_*`;
- hostname apontando para o nome do container/serviço Docker;
- portas explícitas;
- credenciais e nomes lógicos versionados no arquivo central;
- URL derivada opcional, sem substituir as variáveis-base quando elas já existirem.

### 4.4. Autenticação JWT

Quando o backend usar autenticação com JWT, a política de timeout também deve ficar no arquivo central de configuração.

```env
JWT_ACCESS_TOKEN_MINUTES=30
JWT_REFRESH_TOKEN_DAYS=7
JWT_ROTATE_REFRESH_TOKENS=false
```

Diretrizes:

- `access token` deve usar timeout curto;
- `refresh token` deve usar timeout mais longo;
- a aplicação deve ler esses valores em `settings.py`;
- a política não deve ficar implícita no default da biblioteca.

## 5. Convenções de nome

- Use nomes em caixa alta com `_`.
- Prefira prefixos por domínio técnico: `DB_*`, `POSTGRES_*`, `REDIS_*`, `MINIO_*`.
- Evite nomes genéricos demais, como `HOST`, `PORT`, `USER` ou `PASSWORD`.
- Sempre que possível, mantenha o nome da variável estável entre local, homologação e produção.

## 6. Regras para Docker Compose

- O `docker-compose` deve consumir o mesmo arquivo central de configuração usado pela aplicação.
- Nomes de serviços devem ser previsíveis e curtos, como `postgres`, `redis` e `minio`.
- Não replique valores literais em múltiplos lugares se eles já existem no arquivo central.
- Se o compose precisar de valores exclusivos de infraestrutura, documente-os junto com as demais variáveis deste arquivo.

## 7. Resultado esperado

Quando este padrão for seguido:

- o backend sobe com configuração previsível;
- serviços Docker ficam acessíveis por nomes estáveis;
- banco, cache e storage não dependem de valores hardcoded;
- novos serviços podem ser adicionados sem desorganizar a configuração do projeto.
