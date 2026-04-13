# Arquitetura do Backend (Django + DRF)

**Descrição**: Este é o documento-mãe do backend no PAIA. Ele define a estrutura obrigatória do projeto, registra decisões transversais e aponta para os instructs especializados de cada camada. Regras detalhadas de implementação não devem ser duplicadas aqui.

---

## 1. Papel deste arquivo

Este arquivo deve ser usado para:

- orientar a criação e edição de projetos backend no padrão do PAIA;
- definir limites entre camadas;
- registrar decisões transversais de arquitetura;
- servir como índice oficial dos documentos especializados do backend.

Este arquivo não deve ser usado para:

- concentrar toda a regra de model, serializer, viewset, action, behavior, task, filter ou manager;
- repetir exemplos extensos já documentados nos instructs específicos;
- virar um repositório de snippets desconectados do restante da documentação.

---

## 2. Estrutura obrigatória do projeto

Todo backend gerado para o PAIA deve ser criado dentro de `artifacts/backend/`.

Estrutura base esperada:

```console
artifacts/
    backend/
        <project_name>/
            manage.py
            <project_name>/
                settings.py
                asgi.py
                wsgi.py
                urls.py
            core/
                __init__.py
                models.py
                serializers.py
                viewsets.py
                actions.py
                exceptions.py
                tasks.py
            accounts/
                __init__.py
                models.py
                serializers.py
                viewsets.py
                actions.py
                messages.py
                exceptions.py
                urls.py
            <domain_app>/
                __init__.py
                models.py
                serializers.py
                viewsets.py
                actions.py
                messages.py
                exceptions.py
                urls.py
```

Diretrizes:

- não criar artefatos de backend fora de `artifacts/backend/`;
- manter o projeto Django separado das apps de domínio;
- tratar `core` como base compartilhada obrigatória para classes, mixins e contratos reutilizáveis;
- tratar `accounts` como app obrigatória para autenticação, usuário, perfil e senha quando o projeto possuir gestão própria de acesso;
- considerar `core` + `accounts` como o skeleton padrão do backend;
- criar novas apps de domínio sobre esse skeleton, reaproveitando `core` e `accounts` em vez de duplicar suas responsabilidades;
- criar novas apps de domínio com arquivos compatíveis com os instructs especializados.

Exemplo de skeleton:

- `core`: base técnica compartilhada;
- `accounts`: autenticação e identidade do usuário;
- `schools`: domínio de gerenciamento de escolas, consumindo `core` e `accounts`.

---

## 3. Decisões transversais de arquitetura

### 3.1. Organização por camadas

- `core/`: camada base obrigatória para contratos compartilhados e infraestrutura de app;
- `accounts/`: camada base obrigatória para autenticação, usuários, perfis, permissões e senha;
- `models.py`: representa entidades e mapeamento relacional;
- `serializers.py`: trata contrato de entrada e saída de dados;
- `viewsets.py`: expõe endpoints e orquestra o fluxo HTTP;
- `actions.py`: concentra mutações síncronas e reutilizáveis do domínio;
- `behaviors.py`: concentra fluxos de domínio mais longos, com múltiplas etapas;
- `tasks.py`: executa processamento assíncrono e delega a regra principal;
- `filters.py`: centraliza filtros declarativos e busca orientada por query string;
- `managers.py`: centraliza consultas reutilizáveis e querysets especializados;
- `messages.py`: centraliza mensagens reutilizáveis de domínio e operação;
- `exceptions.py`: concentra exceções de domínio e erros de contrato.

Regra para apps de domínio:

- toda nova app de negócio deve nascer sobre o skeleton `core` + `accounts`;
- a app de domínio herda bases, mixins e contratos de `core`;
- a app de domínio consome identidade, autenticação, perfil e permissões de `accounts`;
- a app de domínio não redefine base técnica nem autenticação global.

### 3.2. Regra de negócio

- o backend deve usar `actions.py` como fronteira principal da regra de negócio síncrona;
- lógica simples e reutilizável deve preferir `actions`;
- fluxos longos, com muitas etapas ou muito estado intermediário, devem preferir `behaviors`;
- serializers e viewsets não devem concentrar regra de domínio que pertença a `actions` ou `behaviors`.

### 3.3. Banco e persistência

- o banco relacional padrão do PAIA é PostgreSQL 17;
- o projeto não deve depender de SQLite como banco principal;
- models de domínio devem seguir as regras de base, herança, `db_table`, histórico e nomenclatura definidas nos docs de modelagem;
- relações com usuário devem usar `settings.AUTH_USER_MODEL`, e não import direto de `django.contrib.auth.models.User`, fora da app `accounts`;
- migrations fazem parte do contrato do backend e devem ser versionadas.

### 3.4. Configuração operacional

- o backend deve carregar um arquivo de configuração central a partir de `BASE_DIR`, como `bit.conf`, `paia.conf` ou outro `<nome-do-projeto>.conf`;
- variáveis de ambiente devem ser a fonte de verdade para banco, cache, filas, storage e demais serviços;
- credenciais sensíveis não devem ficar hardcoded no código;
- quando o projeto usar senha ou segredo armazenado de forma codificada, a leitura deve passar por helper de descriptografia antes do uso;
- nomes de serviços Docker devem ser estáveis e previsíveis, como `postgres`, `redis` e `minio`.
- quando não existir compose na raiz do projeto, deve ser criada a pasta `compose/` com arquivos separados por serviço e também um `docker-compose.yml` agregador na raiz.

### 3.5. Storage e arquivos

- quando houver storage compatível com S3, o padrão do projeto deve usar `django-storages`;
- `STORAGES`, `STATIC_URL` e `MEDIA_URL` devem ser dirigidos por variáveis `AWS_*`;
- a configuração de MinIO ou S3 compatível deve permanecer centralizada em arquivo de configuração e `settings.py`, nunca espalhada em múltiplos módulos.

### 3.6. HTTP e API

- o backend padrão usa Django REST Framework;
- endpoints devem preferir organização por app e exposição via `urls.py`;
- o roteamento principal deve concentrar os `include(...)` das apps;
- filtros, paginação, autenticação e permissões devem seguir configuração explícita em `settings.py`.
- autenticação, registro, `me` e senha devem ficar sob a app `accounts`.

### 3.7. Assincronicidade

- tarefas assíncronas devem usar Celery;
- processamento pesado, integração externa e jobs longos devem ir para `tasks.py`;
- efeitos externos dependentes de persistência devem ser disparados preferencialmente após commit.

---

## 4. Padrão mínimo de `settings.py`

O `settings.py` de novos projetos deve seguir estes princípios:

- carregar o arquivo de configuração central se ele existir;
- montar `DATABASES` a partir de variáveis `DB_*`;
- tratar segredos de banco e storage fora de valores literais no código;
- configurar storage compatível com S3 por `AWS_*` quando o projeto usar arquivos;
- definir `REST_FRAMEWORK` com autenticação, permissão e paginação explícitas.

Exemplo de pontos obrigatórios:

```python
competence_conf = os.path.join(BASE_DIR, 'bit.conf')

if exists(competence_conf):
    load_dotenv(competence_conf)

ENGINE = os.environ.get('DB_ENGINE')
NAME = os.environ.get('DB_NAME')
HOST = os.environ.get('DB_HOST')
PORT = os.environ.get('DB_PORT')
USER = os.environ.get('DB_USER')
PASSWORD = os.environ.get('DB_PASS')
```

E também:

- descriptografia de `DB_PASS` antes de montar `DATABASES`;
- uso de `AWS_S3_ENDPOINT_URL`, `AWS_S3_ACCESS_KEY_ID`, `AWS_S3_SECRET_ACCESS_KEY` e `AWS_STORAGE_BUCKET_NAME` quando houver storage;
- definição de `STORAGES`, `STATIC_URL` e `MEDIA_URL`;
- configuração explícita de `REST_FRAMEWORK`.

Os detalhes completos de configuração operacional ficam em [conf-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/conf-instruct.md), e as regras do banco ficam em [postgres-17-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/database/postgres-17-instruct.md).

---

## 5. Mapa oficial dos docs de backend

Use este mapa como ponto de entrada para criação e edição de código:

- [architeture-back.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/architeture-back.md): visão geral, limites entre camadas e decisões transversais.
- [frameworks-and-libs.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/frameworks-and-libs.md): stack, bibliotecas permitidas e escolhas técnicas.
- [conf-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/conf-instruct.md): variáveis de ambiente, serviços Docker e configuração operacional.
- [compose-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/compose-instruct.md): padrão para arquivos Docker Compose por serviço e compose agregador na raiz.
- [accounts-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/accounts-instruct.md): app dedicada para autenticação, usuários, perfis, permissões e senha.
- [models-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/models-instruct.md): criação e alteração de models.
- [serializers-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/serializers-instruct.md): criação e alteração de serializers.
- [viewsets-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/viewsets-instruct.md): criação e alteração de viewsets.
- [actions-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/actions-instruct.md): regras para actions.
- [behaviors-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/behaviors-instruct.md): regras para behaviors.
- [tasks-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/tasks-instruct.md): regras para tasks assíncronas.
- [filters-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/filters-instruct.md): regras para filtros.
- [managers-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/managers-instruct.md): regras para managers e querysets.
- [messages-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/messages-instruct.md): centralização de mensagens reutilizáveis.
- [exceptions-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/exceptions-instruct.md): regras para exceções de domínio e contrato.
- [urls-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/urls-instruct.md): estrutura de roteamento principal e inclusão das apps.

Documentos complementares de banco:

- [rules.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/database/rules.md): modelagem, nomenclatura e integridade.
- [postgres-17-instruct.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/database/postgres-17-instruct.md): engine oficial, conexão e operação com PostgreSQL 17.

---

## 6. Fluxo recomendado para criação de app

1. Definir o contrato do módulo: entidade, serializer, endpoints, ações, filtros, tasks e exceções.
2. Validar o skeleton do projeto: `core`, `accounts`, `settings.py`, banco, storage e serviços.
3. Criar ou alinhar a base compartilhada em `core`.
4. Criar ou alinhar autenticação, usuário e senha em `accounts`.
5. Implementar a app de domínio herdando a base de `core` e consumindo o contexto de `accounts`.
6. Registrar rotas no `urls.py` da app e no `urls.py` principal.
7. Validar transação, permissões, performance de query, testes e impacto assíncrono.
8. Atualizar a documentação especializada quando uma nova regra estrutural surgir.

---

## 7. Checklist arquitetural

Ao criar ou revisar um backend, valide:

1. [ ] O projeto está dentro de `artifacts/backend/`.
2. [ ] O `settings.py` carrega arquivo de configuração e usa variáveis de ambiente.
3. [ ] O banco principal está em PostgreSQL e não em SQLite.
4. [ ] A regra de negócio está em `actions.py` ou `behaviors.py`, não espalhada.
5. [ ] O roteamento está centralizado em `urls.py` com `include(...)` por app.
6. [ ] Storage, filas e serviços auxiliares não possuem credenciais hardcoded.
7. [ ] `core` e `accounts` existem como skeleton base do projeto.
8. [ ] Filtros, serializers, viewsets, tasks, managers, messages e exceptions seguem seus respectivos instructs.
9. [ ] Autenticação, usuário e senha estão centralizados em `accounts`, quando aplicável.
10. [ ] O código novo veio acompanhado de testes e, se necessário, atualização dos docs.

---

## 8. Conclusão

O [architeture-back.md](/mnt/c/Users/estevao.silva/PycharmProjects/paia/docs/backend/architeture-back.md) deve permanecer como documento raiz do backend. Ele não substitui os instructs especializados; ele organiza o uso deles e mantém as decisões arquiteturais transversais do projeto.
