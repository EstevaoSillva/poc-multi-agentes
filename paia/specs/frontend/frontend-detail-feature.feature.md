# Feature: Tela de detalhe e formulário frontend

## Objetivo
Definir o contrato de uma tela de detalhe ou formulário baseada nas estruturas compartilhadas do projeto.

## Escopo
- formulário reativo
- modo criar e editar
- recuperação do registro
- persistência
- validação de campos e UX de salvamento

## Regras
- a tela deve preferir a base documentada em `BaseComponentDetailDirective`
- formulários devem usar Reactive Forms
- a tela deve respeitar o fluxo de create/update baseado em rota quando a base exigir isso
- o componente não deve duplicar retrieve, save ou update se a base já cobre o caso

## Contrato técnico mínimo
- `createFormGroup()`
- `endpoint`
- `retrieveOnInit` quando houver edição
- submit reaproveitando a base

## Padrões esperados
- componente standalone quando aplicável
- estado local com `signal` quando houver estado visual complementar
- validação coerente com o contrato do backend
- formulários e carregamento integrados à base compartilhada

## Referências
- `docs/frontend/core/base-component-detail.directive.md`
- `docs/frontend/core/base.service.md`
- `docs/frontend/architeture-front.md`

## Checklist
- o formulário usa a base correta?
- `createFormGroup()` cobre todos os campos esperados?
- a tela respeita o fluxo create/update?
- o submit reutiliza a base em vez de duplicar HTTP?
