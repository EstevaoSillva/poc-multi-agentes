import os
from pathlib import Path

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv

load_dotenv()

infra_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

def backend_infra_agent(backend_dir):
    # Garantir que backend_dir é um Path
    backend_dir = Path(backend_dir) if isinstance(backend_dir, str) else backend_dir
    return Agent(
        name="Backend Infra Agent",
        role="Infraestrutura do backend",
        model=infra_model,
        tools=[FileTools(base_dir=backend_dir), DuckDuckGoTools()],
        instructions=[
            "Você é um desenvolvedor Python senior.",
            "Quando solicitado a criar um arquivo, SEMPRE use a ferramenta 'FileTools' disponível.",
            "A ferramenta FileTools permite: write_file(file_path, content)",
            "IMPORTANTE: Você DEVE usar FileTools para criar/modificar arquivos.",
            "Criar estrutura base do backend.",
            "Criar requirements.txt.",
            "Criar README.md.",
            "NÃO criar banco, modelos ou endpoints.",
            "NUNCA criar pasta raiz do projeto.",
            "Forneça código completo e funcional.",
        ],
    )

