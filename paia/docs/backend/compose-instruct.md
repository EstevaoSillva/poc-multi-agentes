# Guia de Compose para Infraestrutura do Backend

**Descrição**: Este documento define o padrão para criação de arquivos Docker Compose de infraestrutura no PAIA. Ele cobre a organização dos arquivos na pasta `compose/`, o arquivo agregador na raiz e as regras para serviços como PostgreSQL, Redis, MinIO e demais dependências solicitadas pelo projeto.

## 1. Objetivo

- todo projeto que depender de infraestrutura local via Docker deve possuir arquivos Compose previsíveis;
- a infraestrutura deve poder ser subida por serviço isolado e também por um compose agregador na raiz;
- variáveis devem vir preferencialmente do arquivo central de configuração, como `paia.conf`.

## 2. Estrutura obrigatória

Quando não existir compose na raiz do projeto:

- criar a pasta `compose/`;
- criar um arquivo separado por serviço de infraestrutura;
- criar na raiz um `docker-compose.yml` com os mesmos serviços essenciais;
- usar nomes de serviço estáveis, como `postgres`, `redis` e `minio`.

Estrutura esperada:

```console
compose/
    postgres.compose.yml
    redis.compose.yml
    minio.compose.yml
docker-compose.yml
paia.conf
```

## 3. Regra de separação por serviço

- `compose/postgres.compose.yml`: banco relacional;
- `compose/redis.compose.yml`: cache, broker ou backend de resultado;
- `compose/minio.compose.yml`: storage compatível com S3;
- novos serviços devem seguir o mesmo padrão, como `compose/rabbitmq.compose.yml`, `compose/elasticsearch.compose.yml` ou outro nome semântico.

## 4. Regra do compose agregador

- o arquivo `docker-compose.yml` da raiz deve repetir os serviços essenciais do projeto;
- o objetivo do arquivo agregador é permitir subir a infraestrutura principal com um único comando;
- o arquivo da raiz deve manter nomes, portas, volumes e `env_file` coerentes com os arquivos individuais.

## 5. Variáveis de ambiente

- os serviços devem usar `env_file: ./paia.conf` ou caminho equivalente quando o compose estiver na raiz;
- para arquivos dentro de `compose/`, o `env_file` deve apontar para `../paia.conf`;
- se uma imagem exigir aliases específicos, como `POSTGRES_DB` ou `MINIO_ROOT_USER`, essas variáveis devem existir no arquivo central de configuração;
- não duplicar credenciais em múltiplos arquivos sem necessidade.

## 6. Volumes e portas

- PostgreSQL deve ter volume persistente dedicado;
- MinIO deve ter volume persistente dedicado;
- Redis pode usar volume quando o projeto precisar persistência local;
- portas expostas devem ser explícitas e previsíveis:
  - PostgreSQL: `5432`
  - Redis: `6379`
  - MinIO API: `9000`
  - MinIO Console: `9001`

## 7. Redes e nomes de serviço

- os serviços devem compartilhar uma rede padrão do compose;
- o hostname preferencial da aplicação deve ser o nome do serviço;
- os nomes usados no `settings.py` e no `.conf` devem casar com os nomes do compose.

## 8. Resultado esperado

Quando este padrão for seguido:

- a infraestrutura local sobe com previsibilidade;
- o backend encontra banco, cache e storage pelos nomes esperados;
- novos serviços podem ser adicionados sem desorganizar a operação local.
