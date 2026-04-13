# Feature: Criação de app frontend Angular

## Objetivo
Criar uma nova feature frontend no padrão do PAIA, pronta para crescer por domínio sem desalinhar o skeleton `core` + `accounts`, os componentes base, a autenticação e os contratos com backend.

## Escopo
- criar a feature dentro de `artifacts/frontend/`
- alinhar o skeleton base em `core`, `accounts` e `shared`
- estruturar rotas, componentes, services e configurações da feature
- manter coerência com os contratos do backend

## Regras
- a feature deve respeitar `docs/frontend/architeture-front.md`
- componentes novos devem preferir `standalone: true`
- a aplicação deve seguir modo zoneless
- estado local deve preferir `signal`
- formulários devem usar Reactive Forms
- novas features de domínio devem consumir `core` e `accounts`
- autenticação global, sessão e senha não devem ser implementadas fora de `accounts`

## Estrutura esperada
Feature com:
- componente de entrada da feature
- arquivos de rota quando aplicável
- service da feature quando houver integração dedicada
- configurações auxiliares quando a feature usar filtros, colunas ou tabelas
- testes quando o projeto já suportar essa camada

## Contrato técnico mínimo
- o projeto deve existir dentro de `artifacts/frontend/`
- `core` e `accounts` devem existir como skeleton base
- a feature deve reutilizar bases compartilhadas antes de criar abstrações novas
- a rota da feature deve permanecer coerente com o domínio e com o backend

## Entregáveis
- feature criada no local correto
- skeleton `core` + `accounts` alinhado
- rota da feature registrada quando aplicável
- componentes e services preparados para evolução futura

## Checklist
- a feature foi criada dentro de `artifacts/frontend/`?
- o skeleton `core` + `accounts` existe ou foi alinhado?
- a feature reutiliza bases existentes?
- a autenticação não ficou espalhada na feature?
- a estrutura está pronta para crescer sem retrabalho?
