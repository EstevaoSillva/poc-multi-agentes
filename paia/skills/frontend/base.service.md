**Descrição**: Você é especialista em criar e adaptar services HTTP reutilizáveis no frontend com base no `BaseService` do projeto.

## Objetivo

Garantir que features e componentes reutilizem a base de acesso HTTP antes de criar serviços duplicados.

## Fontes de verdade

- `docs/frontend/core/base.service.md`
- `docs/frontend/core/base-component-list.directive.md`
- `docs/frontend/core/base-component-detail.directive.md`
- `specs/frontend/frontend-base-service.feature.md`

## Checklist

- O service concreto reaproveita a base.
- CRUD e paginação estão coerentes com o contrato da base.
- URL, params e headers não foram duplicados sem necessidade.
- O componente não chamou `HttpClient` diretamente quando a base já cobria o caso.


