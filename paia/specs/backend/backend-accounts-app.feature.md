# Feature: App accounts do backend

## Objetivo
Definir o contrato estrutural da app `accounts`, responsável por autenticação, cadastro, usuários, perfis, permissões e fluxos de senha.

## Escopo
- autenticação por login e refresh token
- registro de usuário
- endpoint do usuário autenticado
- gestão de perfil e papéis
- mudança de senha
- recuperação ou redefinição de senha quando aplicável

## Regras
- a autenticação global do backend deve ficar em `accounts`
- `accounts` compõe o skeleton obrigatório do backend junto com `core`
- a app deve possuir `models.py`, `serializers.py`, `viewsets.py`, `actions.py`, `messages.py`, `exceptions.py` e `urls.py`
- quando o projeto nascer com autenticação própria, deve usar `AUTH_USER_MODEL = "accounts.User"`
- apps de domínio devem referenciar usuário por `settings.AUTH_USER_MODEL`
- `django.contrib.auth.models.User` não deve ser importado diretamente em apps de domínio
- regras de escrita devem ficar em `actions.py`
- mensagens e exceções devem ser centralizadas

## Entregáveis
- app `accounts` criada
- modelo `User` ou estratégia explícita para usuário
- modelo de perfil ou papéis quando necessário
- serializers de login, registro, `me` e senha
- serializers de recuperação e redefinição de senha quando o fluxo existir
- endpoints de autenticação e usuário
- rotas sob `/api/accounts/`
- testes unitários e de API

## Contrato mínimo de API
- `POST /api/accounts/login/`
- `POST /api/accounts/token/refresh/`
- `POST /api/accounts/register/`
- `GET /api/accounts/me/`
- `POST /api/accounts/change-password/`

## Referências
- `docs/backend/accounts-instruct.md`
- `docs/backend/serializers-instruct.md`
- `docs/backend/viewsets-instruct.md`
- `docs/backend/actions-instruct.md`
- `docs/backend/messages-instruct.md`
- `docs/backend/exceptions-instruct.md`
- `docs/backend/urls-instruct.md`

## Checklist
- `accounts` está tratada como parte do skeleton do projeto?
- a autenticação saiu de `core` e das apps de domínio?
- a app `accounts` concentra login, registro e senha?
- o projeto usa `AUTH_USER_MODEL` quando necessário?
- as outras apps só consomem usuário, sem duplicar autenticação?
