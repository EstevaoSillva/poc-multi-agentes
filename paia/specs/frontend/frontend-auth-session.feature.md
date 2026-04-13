# Feature: Autenticação e sessão no frontend

## Objetivo
Definir o contrato da camada de autenticação e sessão do frontend, centralizada em `accounts`, com login, refresh token, usuário autenticado, logout e recuperação de sessão.

## Escopo
- tela de login
- service de sessão
- persistência de access token e refresh token
- leitura do usuário autenticado
- refresh token
- logout e limpeza de sessão

## Regras
- autenticação deve ficar em `accounts`
- login deve consumir o backend em `/api/accounts/`
- tokens devem ser persistidos por camada própria de sessão
- o frontend deve conseguir restaurar sessão existente
- o usuário autenticado deve ficar exposto por `signal` ou contrato equivalente
- refresh token deve respeitar a política do backend

## Contratos mínimos
- método de login
- método de refresh token
- método de logout
- método de leitura do usuário autenticado
- método de verificação de sessão

## Padrões esperados
- componentes standalone
- estado local com `signal`
- `inject(...)` quando o padrão do projeto permitir
- integração com guards e roteamento
- mensagens e UX coerentes em falha de autenticação

## Referências
- `docs/frontend/architeture-front.md`
- `docs/frontend/accounts/auth-component-instruct.md`
- `docs/frontend/accounts/auth.service.md`
- `specs/features/login.feature.md`
- `specs/features/password-recovery.feature.md`

## Checklist
- login, refresh e logout estão centralizados em `accounts`?
- tokens são persistidos e limpos corretamente?
- o frontend consegue recuperar o usuário autenticado?
- a sessão não foi espalhada em múltiplas features?
