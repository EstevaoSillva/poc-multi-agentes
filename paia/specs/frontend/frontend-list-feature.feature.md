# Feature: Tela de listagem frontend

## Objetivo
Definir o contrato de uma tela de listagem frontend baseada nas estruturas compartilhadas do projeto.

## Escopo
- tabela ou lista paginada
- filtros livres e por coluna
- ordenação
- integração com endpoint backend
- ações como delete, toggle, export ou associação quando existirem

## Regras
- a listagem deve preferir a base documentada em `BaseComponentListDirective`
- a tela deve prever paginação
- a fonte de dados deve permanecer coerente com a base compartilhada
- o componente não deve duplicar lógica já coberta pela base
- a feature deve consumir `core` e `accounts` quando depender de sessão ou contexto de usuário

## Contrato técnico mínimo
- `displayedColumns`
- `endpoint`
- `searchOnInit` quando aplicável
- filtros coerentes com a API
- integração com paginação e ordenação

## Padrões esperados
- listagem standalone quando aplicável
- service reutilizado da base
- filtros compatíveis com backend
- ações de linha reaproveitando os helpers da base

## Referências
- `docs/frontend/core/base-component-list.directive.md`
- `docs/frontend/core/base.service.md`
- `docs/frontend/architeture-front.md`

## Checklist
- a listagem usa a base correta?
- a paginação está prevista?
- os filtros correspondem à API real?
- a tela evita reimplementar a busca?
