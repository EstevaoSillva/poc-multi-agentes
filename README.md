# POC Multi-Agentes (Django + Agno + Ollama)

Este projeto é uma prova de conceito de um **copiloto multi-agente** para criar e evoluir projetos de software a partir de prompts em linguagem natural.

A aplicação expõe uma API Django/DRF que:
- cria sessões de projeto,
- interpreta intenção do usuário,
- planeja ações,
- executa ferramentas no workspace da sessão,
- registra histórico e trilha de auditoria,
- suporta execução com streaming via WebSocket.

## O que o projeto faz

- **Ideação de app**: interpreta um prompt e sugere nome, categoria e stack.
- **Geração inicial de projeto**: cria scaffold backend/frontend com base em planejamento.
- **Edição assistida**: para cada nova interação, classifica intenção, gera plano e executa tools.
- **Aprovação de ações destrutivas**: `write_file` e `delete_file` exigem confirmação.
- **Memória de sessão + RAG local**:
  - persiste interações em `workspace/sessions/session_<id>/memory.json`;
  - indexa conhecimento em vetores locais (`vectors/`) e recupera contexto relevante.
- **Streaming em tempo real**: envia eventos de progresso para clientes WebSocket.

## Como funciona (arquitetura)

### Componentes principais

- `multi_agentes/`: configuração Django/ASGI.
- `agents_app/orchestrator.py`: orquestrador central (`CopilotOrchestrator`).
- `agents_app/agents/`: agentes do pipeline principal (roteador de intenção, planner, geração, revisão, guard de execução).
- `agents_app/tools/`: registry/broker de ferramentas e políticas de execução.
- `agents_app/services/`: geração de projeto, memória de sessão, embeddings e ingestão de conhecimento.
- `agents_app/api/`: models, serializers e endpoints REST.
- `agents_app/streaming/`: consumer e serviço de eventos WebSocket.
- `workspace/`: diretório de saída dos projetos por sessão.

### Fluxo resumido de execução

1. Usuário envia prompt.
2. Sistema identifica intenção (`GENERATE`, `MODIFY`, etc.).
3. Planner monta estratégia (`chat_only` ou `execute_tools`).
4. Se houver tool destrutiva, cria `PendingAction` e aguarda aprovação.
5. Executa tools permitidas no workspace isolado da sessão.
6. Gera/responde com apoio de memória + contexto RAG.
7. Persiste `Interaction`, `ToolExecution` e atualização da memória.

## Pré-requisitos

- Python 3.12+
- Docker + Docker Compose
- Ollama instalado localmente

## Configuração

### 1) Clonar e instalar dependências

```bash
git clone <url-do-repo>
cd poc-multi-agentes
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

No Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Configurar variáveis de ambiente (`mult.conf`)

O projeto carrega automaticamente o arquivo `mult.conf` na raiz.

Exemplo:

```env
DB_ENGINE=django.db.backends.postgresql
DB_HOST=localhost
DB_PORT=5434
DB_NAME=postgres
DB_USER=postgres
DB_PASS=123456

DEBUG=True

WORKSPACE_PATH=./workspace

OLLAMA_CHAT_MODEL=llama3:8b
OLLAMA_CODE_MODEL=qwen2.5-coder:7b-instruct
OLLAMA_FALLBACK_MODEL=qwen2.5-coder:7b-instruct

# Opcional (RAG)
KNOWLEDGE_AUTO_INDEX=True
KNOWLEDGE_SOURCES=/caminho/docs,/caminho/skills,/caminho/specs
```

Observações:
- `WORKSPACE_PATH` é opcional; padrão: `./workspace`.
- `KNOWLEDGE_SOURCES` é opcional. Se não informado, usa paths padrão relativos a `../paia`.
- As variáveis AWS/MinIO podem ficar definidas, mas o fluxo principal atual não depende delas.

### 3) Subir PostgreSQL

```bash
docker compose -f compose/docker-compose-postgres.yml up -d
```

### 4) Preparar banco

```bash
python manage.py migrate
python manage.py createsuperuser  # opcional
```

### 5) Baixar modelos do Ollama

```bash
ollama pull llama3:8b
ollama pull qwen2.5-coder:7b-instruct
```

## Como executar

### API HTTP

```bash
python manage.py runserver
```

API disponível em: `http://127.0.0.1:8000`

### Com ASGI (recomendado para carga WebSocket)

```bash
daphne -b 0.0.0.0 -p 8000 multi_agentes.asgi:application
```

## Endpoints principais

Base: `http://127.0.0.1:8000/api/`

- `POST /api/ideation/`
  - interpreta ideia e cria sessão.
- `POST /api/copilot/`
  - fluxo completo: ideação + criação de sessão + start.
- `POST /api/sessions/{id}/interact/`
  - envia novas interações para a sessão.
- `POST /api/pending-actions/{id}/approve/`
  - aprova ação destrutiva pendente.
- `POST /api/pending-actions/{id}/reject/`
  - rejeita ação destrutiva.
- `POST /api/sessions/{id}/knowledge/reindex/`
  - reindexa fontes de conhecimento.
- `GET /api/sessions/{id}/knowledge/stats/`
  - estatísticas do índice vetorial.

Recursos CRUD/listagem (DRF router):
- `/api/sessions/`
- `/api/interactions/`
- `/api/tool-executions/`
- `/api/pending-actions/`

## Exemplo rápido de uso (REST)

### 1) Ideação

```bash
curl -X POST http://127.0.0.1:8000/api/ideation/ \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Quero um sistema de tarefas com dashboard"}'
```

### 2) Interagir com a sessão

```bash
curl -X POST http://127.0.0.1:8000/api/sessions/1/interact/ \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Adicione autenticação JWT no backend"}'
```

## Streaming WebSocket

Rota:

```text
ws://127.0.0.1:8000/ws/stream/<session_id>/
```

Payload de execução:

```json
{
  "action": "run",
  "session_id": 1,
  "user_input": "Crie endpoints REST para produtos"
}
```

Cliente de teste disponível em:
- `agents_app/testes/test_streaming_client.py`

Execução:

```bash
python agents_app/testes/test_streaming_client.py 1 "Create a REST API backend"
```

## Estrutura do workspace por sessão

```text
workspace/
  sessions/
    session_<id>/
      backend/
      frontend/
      shared/
      logs/
      memory.json
      vectors/
        index.faiss
        metadata.json
        knowledge_state.json
```

## Auditoria e segurança

- Toda execução de tool gera registro em `ToolExecution`.
- Interações são registradas em `Interaction`.
- Ações destrutivas entram em `PendingAction` e exigem aprovação explícita.
- Há validação de sandbox para impedir acesso fora do workspace da sessão.

## Testes

Testes Django:

```bash
python manage.py test
```

Existem também scripts de teste manual em `agents_app/testes/`.

## Troubleshooting

- **Erro de conexão com banco**:
  - confirme PostgreSQL ativo em `localhost:5434`;
  - valide `DB_*` em `mult.conf`.
- **Modelo Ollama não encontrado**:
  - execute `ollama pull` para os modelos configurados em `OLLAMA_*`.
- **Sem resultados de RAG**:
  - confira `KNOWLEDGE_SOURCES` e rode reindex:
  - `POST /api/sessions/{id}/knowledge/reindex/`.
- **WebSocket não conecta**:
  - confira rota `/ws/stream/<session_id>/`;
  - prefira execução via `daphne`.

## Status do projeto

POC em evolução. A API e os fluxos de orquestração estão funcionais para desenvolvimento local e experimentação.
