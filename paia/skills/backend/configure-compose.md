**Descrição**: Você é especialista em criar arquivos Docker Compose de infraestrutura no padrão do PAIA.

## Objetivo

Gerar arquivos de compose por serviço em `compose/` e também um `docker-compose.yml` agregador na raiz, usando o arquivo central de configuração.

## Fontes de verdade

- `docs/backend/compose-instruct.md`
- `docs/backend/conf-instruct.md`
- `docs/backend/architeture-back.md`
- `specs/backend/backend-compose-services.feature.md`

## Checklist

- Existe pasta `compose/`.
- Existe arquivo separado para `postgres`, `redis` e `minio`.
- Existe `docker-compose.yml` na raiz.
- Os arquivos usam `paia.conf`.
- Os nomes de host batem com o que o backend espera.
