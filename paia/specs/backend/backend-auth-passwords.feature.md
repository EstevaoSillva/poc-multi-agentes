# Feature: Autenticação e ciclo de senha

## Objetivo
Definir o contrato funcional de login, refresh token, registro, alteração de senha e redefinição de senha na app `accounts`.

## Regras
- login deve aceitar credenciais válidas e retornar tokens no padrão do projeto
- refresh token deve permitir renovação de sessão sem novo login
- access token deve possuir tempo de vida explícito em minutos
- refresh token deve possuir tempo de vida explícito em dias
- a política de timeout deve ser configurável por ambiente
- registro deve criar usuário com senha segura
- mudança de senha deve exigir senha atual quando o usuário troca a própria senha
- redefinição de senha deve usar token próprio e prazo de validade
- mensagens de erro devem ser consistentes para credenciais inválidas, senha fraca, token inválido e permissão negada

## Endpoints mínimos
- `POST /api/accounts/login/`
- `POST /api/accounts/token/refresh/`
- `POST /api/accounts/register/`
- `POST /api/accounts/change-password/`

## Endpoints opcionais
- `POST /api/accounts/forgot-password/`
- `POST /api/accounts/reset-password/`

## Fluxos complementares obrigatórios no domínio de autenticação
- cadastro deve seguir `specs/features/register.feature.md`
- recuperação e redefinição de senha devem seguir `specs/features/password-recovery.feature.md`

## Padrões esperados
- uso de JWT quando o projeto adotar autenticação stateless
- configuração explícita de `SIMPLE_JWT`
- uso de `JWT_ACCESS_TOKEN_MINUTES` e `JWT_REFRESH_TOKEN_DAYS`
- uso de `set_password(...)` ou caminho seguro equivalente
- validação por serializers dedicados
- delegação da mutação para `actions.py`
- mensagens em `messages.py`
- exceções em `exceptions.py`

## Referências
- `docs/backend/accounts-instruct.md`
- `docs/backend/frameworks-and-libs.md`
- `docs/backend/messages-instruct.md`
- `docs/backend/exceptions-instruct.md`

## Checklist
- login e refresh possuem contratos estáveis?
- o timeout de access token está explícito?
- o timeout de refresh token está explícito?
- a senha nunca é tratada fora do fluxo seguro do Django?
- mudança de senha valida senha atual?
- reset de senha usa token com validade?
- os erros retornados são previsíveis para frontend e integração?
