import os
from pathlib import Path

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv

load_dotenv()

dev_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

def frontend_dev_agent(frontend_dir):
    # Garantir que frontend_dir é um Path
    frontend_dir = Path(frontend_dir) if isinstance(frontend_dir, str) else frontend_dir
    return Agent(
        name="Frontend Dev Agent",
        role="Desenvolvimento da interface",
        model=dev_model,
        tools=[FileTools(base_dir=frontend_dir), DuckDuckGoTools()],
        instructions=[
            "Você é um desenvolvedor web senior.",
            "Quando solicitado a criar um arquivo, SEMPRE use a ferramenta 'FileTools' disponível.",
            "A ferramenta FileTools permite: write_file(file_path, content)",
            "IMPORTANTE: Você DEVE usar FileTools para criar/modificar arquivos.",
            "Implementar interface de lista de tarefas.",
            "Usar apenas HTML5, CSS3 e JavaScript puro.",
            "Consumir API REST em http://127.0.0.1:8000.",
            "Implementar CRUD completo.",
            "Não alterar estrutura criada pelo Infra Agent.",
            "Não criar novos arquivos sem necessidade.",
            "Não criar README.",
            "Forneça código completo e funcional.",
        ],
    )
