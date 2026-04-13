# Feature: Registro de rotas da app backend

## Objetivo
Garantir que uma nova app backend seja exposta de forma padronizada no roteamento principal do Django.

## Regras
- Cada app deve ter seu próprio `urls.py`.
- O arquivo principal do projeto deve incluir a app com `include('nome_da_app.urls')`.
- As rotas devem ficar sob prefixo `/api/`.
- Caminhos específicos devem aparecer antes dos genéricos.
- Endpoints administrativos ou internos não devem ser expostos sem necessidade.
- O `urls.py` da app deve expor apenas as rotas do seu domínio.

## Estrutura
Rotas da app:
- listagem
- detalhe
- criação
- atualização parcial
- exclusão

Rotas do projeto:
- include da app no `urls.py` principal
- manutenção das rotas administrativas e de health quando existirem

## Backend
Exemplo de inclusão:
- `path('api/<app>/', include('<app>.urls'))`

Documentação base:
- `docs/backend/urls-instruct.md`
- `docs/backend/architeture-back.md`

## Contrato mínimo
- `urls.py` principal com `include(...)`
- `urls.py` da app com router DRF quando aplicável
- coerência entre nome da app, prefixo da rota e basename do router

## Checklist
- A app possui `urls.py` próprio?
- O `urls.py` principal inclui a app?
- O prefixo da rota segue o padrão `/api/`?
- A ordem das rotas evita conflito entre paths específicos e genéricos?
- O `basename` e o prefixo do router estão coerentes com o domínio?
