import os
from pathlib import Path

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv

load_dotenv()

db_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

def backend_db_agent(backend_dir):
    # Garantir que backend_dir é um Path
    backend_dir = Path(backend_dir) if isinstance(backend_dir, str) else backend_dir
    return Agent(
        name="Backend Database Agent",
        role="Banco de dados e ORM",
        model=db_model,
        tools=[FileTools(base_dir=backend_dir), DuckDuckGoTools()],
        instructions=[
            "Você é um desenvolvedor Python senior.",
            "Quando solicitado a criar um arquivo, SEMPRE use a ferramenta 'FileTools' disponível.",
            "A ferramenta FileTools permite: write_file(file_path, content)",
            f"IMPORTANTE: Você DEVE usar FileTools para criar/modificar arquivos aqui {backend_dir}.",
            "Configurar SQLite com SQLAlchemy.",
            "Usar Path(__file__) para caminho do banco.",
            "Criar models e engine.",
            "NÃO criar endpoints.",
            "Forneça código completo e funcional.",
        ],
    )

