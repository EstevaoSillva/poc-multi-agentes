# PoC Multi-Agentes

Um projeto de Prova de Conceito para coordenação de múltiplos agentes de IA especializados em diferentes domínios (backend, frontend, produto), com suporte a GPU para acelerar processamento.

## 🎯 Objetivo

Criar uma arquitetura escalável com **times de agentes** colaborativos que podem:
- Trabalhar em paralelo em diferentes tarefas
- Acessar múltiplas LLMs (OpenAI, Groq, Ollama, etc.)
- Executar tarefas com suporte a GPU (NVIDIA)
- Gerenciar estado em banco de dados

---

## 📋 Estrutura do Projeto

```
poc-multi-agentes/
├── agents/                    # Definição dos agentes
│   ├── backend/              # Agentes de backend
│   │   ├── database.py       # Operações com DB
│   │   ├── development.py    # Desenvolvimento backend
│   │   ├── infra.py          # Infraestrutura
│   │   ├── test.py           # Testes
│   │   └── device.py         # 🚀 GPU helper
│   └── frontend/             # Agentes de frontend
│       ├── development.py    # Desenvolvimento frontend
│       ├── infra.py          # Infraestrutura frontend
│       └── test.py           # Testes
│
├── teams/                     # Coordenação entre agentes
│   ├── backend_team.py       # Time de backend
│   ├── frontend_team.py      # Time de frontend
│   └── product_team.py       # Time de produto
│
├── my_app/                   # Aplicação principal
│   ├── backend/              # Backend (FastAPI)
│   └── frontend/             # Frontend
│
├── scripts/
│   └── test_gpu.py          # 🚀 Teste GPU
│
├── main.py                   # Entry point
├── requirements.txt          # Dependências pip
├── GPU_SETUP.md             # 🚀 Guia de GPU
└── README.md                # Este arquivo
```

---

## 🚀 Quick Start

### 1. Criar Virtual Environment

```bash
python3 -m venv mult-agent
source mult-agent/bin/activate
```

### 2. Instalar Dependências

```bash
# Atualizar pip
python -m pip install --upgrade pip setuptools wheel

# Instalar requirements base
pip install -r requirements.txt

# Instalar PyTorch com GPU (CUDA 13.0) *** VERIFIQUE A VERSÃO DO SEU CUDA. Comando: nvidia-smi
python -m pip install --index-url https://download.pytorch.org/whl/cu130 torch torchvision torchaudio --extra-index-url https://pypi.org/simple
```

### 3. Verificar GPU (Opcional)

```bash
python3 scripts/test_gpu.py
```

Saída esperada:
```
nvidia-smi output:
 GPU 0: NVIDIA GeForce RTX 3050 Laptop GPU (...)
torch.cuda.is_available(): True
Device: NVIDIA GeForce RTX 3050 Laptop GPU
```

### 4. Rodar a Aplicação

```bash
python3 main.py
```

---

## 🔧 Configuração de Ambiente

### Criar arquivo .env

Crie um arquivo `.env` na raiz do projeto com suas chaves de API:

```bash
# LLMs
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# Banco de dados (opcional)
DATABASE_URL=sqlite:///./app.db

# GPU (opcional)
CUDA_VISIBLE_DEVICES=0
```

---

## 🤖 Como Usar os Agentes

### Exemplo Básico

```python
from agents.backend import development
from agents.backend.device import get_torch_device

# Obter device (GPU se disponível)
device = get_torch_device()

# Criar agente
agent = development.create_agent()

# Executar tarefa
result = agent.run("Sua tarefa aqui")
print(result)
```

### Com Modelos PyTorch

```python
from agents.backend.device import get_torch_device
import torch

device = get_torch_device()

# Carregar/criar modelo
model = torch.nn.Linear(10, 5).to(device)

# Processar dados
x = torch.randn(32, 10).to(device)
output = model(x)
```

Veja [GPU_SETUP.md](GPU_SETUP.md) para mais exemplos e detalhes.

---

## 🗄️ Banco de Dados

O projeto usa **SQLAlchemy + SQLModel** para ORM:

```python
from agents.backend.database import get_session

with get_session() as session:
    # Suas queries aqui
    pass
```

---

## 📚 Dependências Principais

| Pacote | Uso |
|--------|-----|
| `agno` | Framework para agentes |
| `fastapi` | API web |
| `sqlalchemy` / `sqlmodel` | ORM |
| `openai` | Integração OpenAI |
| `groq` | Integração Groq |
| `ollama` | Integração Ollama |
| `torch` | 🚀 GPU/ML (PyTorch) |
| `pydantic` | Validação |
| `typer` | CLI |

---

## 🚀 Performance com GPU

Para tarefas intensivas em ML:

1. **Usar GPU:**
   ```python
   from agents.backend.device import get_torch_device
   device = get_torch_device()
   model.to(device)
   ```

2. **Monitorar:**
   ```bash
   watch -n 0.5 nvidia-smi
   ```

3. **Liberar memória:**
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

---

## 📖 Documentação Completa

- **[GPU_SETUP.md](GPU_SETUP.md)** – Guia detalhado sobre GPU, exemplos, troubleshooting
- **[agents/backend/device.py](agents/backend/device.py)** – Helper module para GPU

---

## 🧪 Testes

```bash
# Testar GPU
python3 scripts/test_gpu.py

# Testes do projeto (quando implementados)
python3 -m pytest agents/backend/test.py
```

---

## 🔗 Integrações Suportadas

- **LLMs:** OpenAI, Groq, Ollama
- **Busca:** DuckDuckGo
- **Banco de Dados:** SQLite, PostgreSQL
- **GPU:** NVIDIA (CUDA 13.0+)

---

## 🛠️ Troubleshooting

### GPU não detectada
```bash
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"
```

### Erro de memória na GPU
```python
import torch
torch.cuda.empty_cache()
```

Veja [GPU_SETUP.md](GPU_SETUP.md) para mais troubleshooting.

---

**Última atualização:** 19 de dezembro de 2025

Sucesso! 🚀

