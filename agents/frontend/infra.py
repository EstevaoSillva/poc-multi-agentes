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

def frontend_infra_agent(frontend_dir):
    # Garantir que frontend_dir é um Path
    frontend_dir = Path(frontend_dir) if isinstance(frontend_dir, str) else frontend_dir
    return Agent(
        name="Frontend Infra Agent",
        role="Infraestrutura do frontend",
        model=infra_model,
        tools=[FileTools(base_dir=frontend_dir), DuckDuckGoTools()],
        instructions=[
            "Você é um desenvolvedor web senior.",
            "Quando solicitado a criar um arquivo, SEMPRE use a ferramenta 'FileTools' disponível.",
            "A ferramenta FileTools permite: write_file(file_path, content)",
            "IMPORTANTE: Você DEVE usar FileTools para criar/modificar arquivos.",
            "Criar estrutura base do frontend.",
            "Criar index.html, styles.css e app.js vazios.",
            "Criar README.md com instruções de execução.",
            "NÃO implementar lógica de negócio.",
            "NÃO consumir API.",
            "NUNCA criar pastas fora do diretório base.",
            "Todos os arquivos devem estar em UTF-8.",
            "Forneça código completo e funcional.",
        ],
    )
