# Feature: Recuperação e redefinição de senha

## Objetivo
Permitir que o usuário solicite recuperação de senha e conclua a redefinição com token válido, sem expor dados sensíveis.

## Regras
- o fluxo deve ser dividido entre solicitação de recuperação e redefinição final
- a solicitação não deve vazar se o email ou usuário existe na base
- o token de recuperação deve possuir validade explícita
- redefinição deve exigir token válido, nova senha e confirmação quando aplicável
- o token deve ser inutilizado após uso, quando o mecanismo adotado suportar isso
- mensagens de erro devem ser consistentes para token inválido, expirado e payload inválido

## Backend
Endpoints esperados:
- `POST /api/accounts/forgot-password/`
- `POST /api/accounts/reset-password/`

Payload de solicitação:

```json
{
  "email": "user@example.com"
}
```

Payload de redefinição:

```json
{
  "token": "string",
  "password": "string",
  "password_confirm": "string"
}
```

Respostas esperadas:
- resposta neutra na solicitação de recuperação
- confirmação de senha alterada na redefinição
- erro padronizado para token inválido, expirado ou senha inválida

## Padrões esperados
- fluxo centralizado na app `accounts`
- token com validade explícita
- serializers específicos por etapa
- mutação delegada para `actions.py` ou `behaviors.py`
- envio de email ou notificação desacoplado em `tasks.py` quando houver assíncrono

## Checklist
- a solicitação não revela existência do usuário?
- o token tem validade explícita?
- a redefinição invalida ou consome o token corretamente?
- a nova senha passa pelos validadores esperados?
- os erros retornados são previsíveis para frontend e integrações?
