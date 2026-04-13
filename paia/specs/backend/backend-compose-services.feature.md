# Feature: Compose de infraestrutura do backend

## Objetivo
Padronizar a criação de arquivos Docker Compose para serviços de infraestrutura do backend, permitindo subir serviços isolados e também toda a stack principal com um único compose na raiz.

## Regras
- se não existir compose na raiz, criar a pasta `compose/`
- criar um arquivo separado por serviço, como PostgreSQL, Redis e MinIO
- criar na raiz um `docker-compose.yml` com os mesmos serviços essenciais
- usar `paia.conf` como fonte de variáveis sempre que possível
- nomes de serviços devem ser estáveis, como `postgres`, `redis` e `minio`

## Estrutura esperada
- `compose/postgres.compose.yml`
- `compose/redis.compose.yml`
- `compose/minio.compose.yml`
- `docker-compose.yml`
- `paia.conf`

## Serviços mínimos
- PostgreSQL
- Redis
- MinIO

## Comportamentos esperados
- PostgreSQL sobe com volume persistente
- Redis sobe acessível pelo hostname `redis`
- MinIO sobe com API e console
- o compose da raiz sobe a infraestrutura principal com um único comando

## Referências
- `docs/backend/compose-instruct.md`
- `docs/backend/conf-instruct.md`
- `docs/backend/architeture-back.md`

## Checklist
- existe pasta `compose/`?
- existe arquivo individual por serviço?
- existe `docker-compose.yml` na raiz?
- os arquivos usam `paia.conf`?
- hostnames e portas estão coerentes com o backend?
