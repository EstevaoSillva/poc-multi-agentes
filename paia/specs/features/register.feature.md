# Feature: Cadastro de usuário

## Objetivo
Cadastrar um novo usuário pela app `accounts` com validação de identidade, senha segura e criação consistente de perfil.

## Regras
- o payload de cadastro deve ser validado por serializer próprio
- senha e confirmação de senha devem ser consistentes quando o contrato exigir confirmação
- o fluxo deve validar unicidade de username e email quando aplicável
- a senha deve ser persistida apenas por `set_password(...)` ou caminho seguro equivalente
- criação de perfil, papel e dados complementares deve ocorrer no mesmo fluxo transacional quando fizer parte do contrato
- mensagens de erro de cadastro devem ser consistentes

## Backend
Endpoints mínimos:
- `POST /api/accounts/register/`

Payload mínimo esperado:

```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "password_confirm": "string"
}
```

Campos adicionais opcionais:
- `first_name`
- `last_name`
- `role`
- campos de perfil

Respostas esperadas:
- usuário criado
- perfil criado quando aplicável
- erro padronizado para duplicidade, senha inválida ou payload inconsistente

## Padrões esperados
- fluxo centralizado na app `accounts`
- validação por serializer dedicado
- escrita delegada para `actions.py`
- senha nunca exposta no response
- mensagens e exceções centralizadas

## Checklist
- o endpoint de cadastro aceita o payload esperado?
- username e email são validados corretamente?
- a senha é salva pelo mecanismo seguro do Django?
- o response retorna apenas os dados permitidos?
- os erros são previsíveis para frontend e integrações?
