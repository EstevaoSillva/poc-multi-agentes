import os
from agno.models.groq import Groq
from agno.agent import Agent
from agno.tools.file import FileTools # Ferramenta essencial para escrever código
from pathlib import Path

backend_model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_BACKEND_KEY")
)

PROJECT_ROOT = Path("my_app").resolve()
BACKEND_ROOT = PROJECT_ROOT / "backend"

BACKEND_ROOT.mkdir(parents=True, exist_ok=True)

# 1. Agente de Backend
backend_agent = Agent(
    name="Backend Engineer",
    role="Desenvolvedor sênior de API e Banco de Dados",
    model=backend_model,
    tools=[FileTools(base_dir=BACKEND_ROOT)], # Onde ele pode salvar arquivos
    instructions=[
        "Você DEVE usar a ferramenta FileTools para criar arquivos reais.",
        "Nunca apenas mostre código — sempre salve em arquivos.",
        "Crie todos os diretórios necessários.",
        "Use FastAPI.",
        "O backend DEVE iniciar sem erros com uvicorn.",
        "Use imports absolutos.",
        "Resolva o caminho do banco SQLite usando Path(__file__).",
        "Nunca use sqlite com caminho relativo solto.",
        "Crie o banco automaticamente se não existir.",
        "Crie requirements.txt atualizado.",
        "Todos os arquivos DEVEM estar em UTF-8.",
        "Não leia arquivos existentes; sobrescreva.",
        "Todos os arquivos DEVEM ser criados diretamente no diretório atual (backend).",
        "Não crie subpastas redundantes.",
    ],
    debug_mode=True,
    debug_level=2,
)