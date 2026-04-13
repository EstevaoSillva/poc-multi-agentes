# Guia de Construção da App Accounts para IA

**Descrição**: Este documento define como a IA deve criar ou alterar a app `accounts`, responsável por autenticação, cadastro, senhas, contexto do usuário autenticado e regras transversais de usuário no backend.

## 1. Papel da app `accounts`

A app `accounts` deve concentrar:

- modelo de usuário do projeto, quando o backend nascer com autenticação própria;
- perfil, papéis, preferências e metadados do usuário;
- login, refresh token e, quando necessário, logout;
- registro de usuário;
- alteração de senha;
- recuperação ou redefinição de senha;
- endpoint `me` e demais endpoints de contexto do usuário autenticado;
- regras específicas de permissão e visibilidade ligadas ao usuário.

A app `accounts` não deve:

- concentrar regras de domínio que pertencem a apps de negócio;
- expor CRUD genérico de usuários sem regra de permissão clara;
- duplicar autenticação em `core` ou em apps de domínio.

## 2. Regra arquitetural obrigatória

- autenticação e gestão de usuário devem viver em `accounts`;
- `accounts` faz parte do skeleton base do backend junto com `core`;
- apps de domínio não devem implementar login, registro ou mudança de senha;
- apps de domínio devem nascer sobre `core` + `accounts`, consumindo essas duas camadas;
- apps de domínio devem referenciar o usuário por `settings.AUTH_USER_MODEL`;
- não importar `django.contrib.auth.models.User` diretamente em models de domínio;
- quando o projeto começar do zero e houver autenticação própria, preferir definir `AUTH_USER_MODEL = "accounts.User"` desde o início.

## 3. Estrutura mínima esperada

Quando a app `accounts` existir, a estrutura mínima recomendada é:

```console
accounts/
    __init__.py
    models.py
    serializers.py
    viewsets.py
    actions.py
    messages.py
    exceptions.py
    urls.py
    tests/
```

Arquivos opcionais conforme o caso:

- `filters.py`
- `managers.py`
- `tasks.py`
- `behaviors.py`

## 4. Modelos recomendados

### 4.1. Usuário

Se o projeto exigir autenticação própria, o padrão preferido é usar um modelo customizado:

```python
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass
```

Diretrizes:

- criar o modelo em `accounts/models.py` quando o projeto nascer com autenticação;
- definir `AUTH_USER_MODEL = "accounts.User"` em `settings.py`;
- usar email, username, nome e flags de staff conforme o domínio exigir;
- não trocar `AUTH_USER_MODEL` no meio de um projeto já migrado sem necessidade explícita.

### 4.2. Perfil e regras específicas

Quando houver papéis ou dados adicionais:

- criar `Profile` ou modelo equivalente em `accounts/models.py`;
- manter papéis, preferências e dados complementares fora das apps de negócio;
- regras como secretaria, professor, aluno, operador ou cliente devem nascer em `accounts` e só ser consumidas por outras apps.

## 5. Contratos mínimos de API

Endpoints mínimos recomendados:

- `POST /api/accounts/login/`
- `POST /api/accounts/token/refresh/`
- `POST /api/accounts/register/`
- `GET /api/accounts/me/`
- `POST /api/accounts/change-password/`

Endpoints opcionais conforme o projeto:

- `POST /api/accounts/forgot-password/`
- `POST /api/accounts/reset-password/`
- `GET /api/accounts/users/`
- `PATCH /api/accounts/users/<id>/`
- `PATCH /api/accounts/users/<id>/activate/`
- `PATCH /api/accounts/users/<id>/deactivate/`

Fluxos especializados recomendados:

- login: seguir [login.feature.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/specs/features/login.feature.md)
- cadastro: seguir [register.feature.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/specs/features/register.feature.md)
- recuperação e redefinição de senha: seguir [password-recovery.feature.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/specs/features/password-recovery.feature.md)

## 6. Regras de autenticação

- usar Django REST Framework com JWT quando o projeto seguir autenticação stateless;
- login deve validar credenciais sem espalhar lógica no viewset;
- refresh token deve seguir contrato explícito e estável;
- o backend deve definir timeout explícito para `access token` e `refresh token`;
- o tempo de vida dos tokens deve ser configurável por variável de ambiente;
- mensagens de autenticação inválida devem ser centralizadas em `messages.py`;
- exceções de autenticação e permissão devem ficar em `exceptions.py` quando houver customização.

### 6.1. Política mínima de token

Quando o projeto usar JWT, o padrão recomendado é:

- `access token` curto, em minutos;
- `refresh token` mais longo, em dias;
- tempos configurados por `JWT_ACCESS_TOKEN_MINUTES` e `JWT_REFRESH_TOKEN_DAYS`;
- rotação de refresh token explicitamente configurada, sem comportamento implícito.

Exemplo em `settings.py`:

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "30"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": os.getenv("JWT_ROTATE_REFRESH_TOKENS", "false").lower() == "true",
}
```

Regras:

- não deixar o timeout de token apenas no default da biblioteca;
- documentar a política de expiração para frontend e integrações;
- evitar access token longo demais;
- manter refresh token com prazo suficiente para usabilidade, mas explícito.

## 7. Regras de senha

- nunca persistir senha fora do mecanismo padrão do Django;
- criação de usuário deve usar `set_password(...)` ou serializer equivalente seguro;
- alteração de senha deve validar senha atual quando o usuário autenticado trocar a própria senha;
- redefinição de senha deve usar fluxo tokenizado, nunca senha em texto simples por link ou query string aberta;
- solicitação de recuperação não deve revelar se o usuário existe;
- recuperação e redefinição devem usar serializers separados;
- políticas de senha devem respeitar `AUTH_PASSWORD_VALIDATORS`.

## 8. Regras para serializers, actions e viewsets

- serializers de `accounts` devem validar payloads de login, registro, perfil e senha;
- serializers de recuperação e redefinição devem ser separados por etapa;
- `actions.py` deve concentrar criação de usuário, alteração de senha, ativação, desativação e demais mutações;
- `viewsets.py` deve apenas orquestrar o contrato HTTP;
- regras longas de onboarding, convite, recuperação e integração externa podem ir para `behaviors.py` ou `tasks.py`.

## 9. Regras para outras apps

Apps de domínio devem seguir estas regras quando dependerem de usuário:

- considerar `core` + `accounts` como skeleton obrigatório antes de nascerem;
- herdar bases e contratos reutilizáveis de `core`;
- usar `settings.AUTH_USER_MODEL` em relacionamentos;
- consumir papel, perfil ou contexto do usuário a partir de `accounts`;
- não recriar serializers de login em outras apps;
- não criar rotas como `/api/core/login/` ou `/api/<dominio>/register/` para autenticação global.

## 10. Checklist para a IA

- a autenticação ficou centralizada em `accounts`?
- `AUTH_USER_MODEL` foi definido corretamente quando necessário?
- relações com usuário usam `settings.AUTH_USER_MODEL`?
- login, registro e mudança de senha foram delegados para `actions.py`?
- endpoints de usuário ficaram sob `/api/accounts/`?
- mensagens e exceções de autenticação foram centralizadas?
