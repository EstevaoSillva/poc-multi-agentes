import os

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from dotenv import load_dotenv

load_dotenv()

infra_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

def frontend_infra_agent(frontend_dir):
    return Agent(
        name="Frontend Infra Agent",
        role="Infraestrutura do frontend",
        model=infra_model,
        tools=[FileTools(base_dir=frontend_dir)],
        instructions=[
            "Criar estrutura base do frontend.",
            "Criar index.html, styles.css e app.js vazios.",
            "Criar README.md com instruções de execução.",
            "NÃO implementar lógica de negócio.",
            "NÃO consumir API.",
            "NUNCA criar pastas fora do diretório base.",
            "Todos os arquivos devem estar em UTF-8.",
        ],
    )
