# Feature: Configuração de settings, banco e serviços

## Objetivo
Padronizar a configuração inicial do `settings.py` para novos projetos backend com banco, storage e serviços de infraestrutura.

## Regras
- O projeto deve carregar `paia.conf` a partir de `BASE_DIR` usando `load_dotenv(...)` se o arquivo existir.
- Credenciais sensíveis devem ser lidas por variável de ambiente.
- `DB_PASS` e `AWS_S3_SECRET_ACCESS_KEY` devem ser tratadas por helper de descriptografia antes do uso.
- `DATABASES` deve ser montado a partir de `DB_ENGINE`, `DB_NAME`, `DB_HOST`, `DB_PORT`, `DB_USER` e `DB_PASS`.
- Storage S3 compatível deve usar `django-storages` com `STORAGES`.
- `STATIC_URL` e `MEDIA_URL` devem derivar do endpoint configurado.
- Serviços Docker devem usar hostnames previsíveis como `postgres`, `redis` e `minio`.
- O código não deve repetir valores já presentes no arquivo central de configuração.

## Variáveis mínimas
Banco:
- `DB_ENGINE`
- `DB_NAME`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASS`

Storage:
- `AWS_S3_ENDPOINT_URL`
- `AWS_S3_ACCESS_KEY_ID`
- `AWS_S3_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`

Serviços auxiliares mais comuns:
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_DB`
- `REDIS_PASSWORD`
- `REDIS_URL`
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET`
- `MINIO_USE_SSL`
- `MINIO_REGION`

## Backend
O `settings.py` deve incluir:
- carga de `paia.conf`
- helper `encrypt_password`
- helper `decrypt_password`
- `DATABASES`
- `STORAGES`
- `STATIC_URL`
- `MEDIA_URL`
- `REST_FRAMEWORK`

## Referências
- `docs/backend/architeture-back.md`
- `docs/backend/conf-instruct.md`
- `docs/database/postgres-17-instruct.md`

## Checklist
- O projeto carrega `paia.conf`?
- O banco usa `DB_*`?
- A senha do banco é descriptografada antes do uso?
- O storage usa `AWS_*`?
- Os serviços Docker usam nomes de host estáveis?
- O código não possui credenciais hardcoded?
