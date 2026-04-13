# Feature: Login

## Objetivo
Autenticar o usuário pela app `accounts` e iniciar a sessão com estratégia de access token e refresh token.

## Regras
- nome de usuário é obrigatório
- senha é obrigatória
- deve existir uma ação explícita para entrar
- o frontend deve armazenar o token de forma segura segundo a estratégia adotada pelo projeto
- o fluxo deve prever renovação de sessão por refresh token
- mensagens de erro de autenticação devem ser consistentes

## Tela
Formulário com:
- campo de nome de usuário
- campo de senha
- ação de submit

## Backend
Endpoints:
- `POST /api/accounts/login/`
- `POST /api/accounts/token/refresh/`

Payload de login:

```json
{
  "username": "string",
  "password": "string"
}
```

Payload de refresh:

```json
{
  "refresh": "string"
}
```

Respostas esperadas:
- access token
- refresh token
- erro padronizado para credenciais inválidas

Padrões esperados:
- autenticação via DRF/JWT
- fluxo centralizado na app `accounts`
- mensagens de erro centralizadas quando houver customização
- contrato claro para expiração e renovação de token
- timeout de `access token` e `refresh token` explícito em configuração

## Checklist
- o endpoint de login aceita o payload esperado?
- o endpoint de refresh está disponível?
- erros de autenticação são previsíveis para o frontend?
- a política de refresh token está explícita?
