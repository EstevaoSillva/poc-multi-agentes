# Feature: Base de services HTTP do frontend

## Objetivo
Definir o contrato da base de services HTTP reutilizável do frontend para CRUD, paginação, rotas auxiliares e integrações comuns.

## Escopo
- operações CRUD
- leitura paginada
- parâmetros de busca
- rotas auxiliares de lista e detalhe
- download e choices quando o projeto exigir

## Regras
- a base de services deve concentrar comportamento HTTP compartilhado
- features não devem duplicar `HttpClient` para fluxos já cobertos pela base
- composição de URL, params e headers deve ser consistente
- a API da base deve continuar extensível para serviços concretos

## Padrões esperados
- tipagem explícita
- API moderna e coesa
- integração com as bases de listagem e detalhe
- separação entre configuração de request e lógica de feature

## Referências
- `docs/frontend/core/base.service.md`
- `docs/frontend/core/base-component-list.directive.md`
- `docs/frontend/core/base-component-detail.directive.md`

## Checklist
- a base cobre CRUD e paginação?
- services concretos reaproveitam a base?
- a montagem de params e URL está coerente?
- a feature evitou duplicação de acesso HTTP?
