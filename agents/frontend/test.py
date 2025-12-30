import os

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv

load_dotenv()

test_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

def frontend_test_agent(frontend_dir):
    return Agent(
        name="Frontend Test Agent",
        role="Testes e validação do frontend",
        model=test_model,
        tools=[FileTools(base_dir=frontend_dir), DuckDuckGoTools()],
        instructions=[
            "Validar se a UI carrega corretamente.",
            "Verificar chamadas fetch.",
            "Criar checklist de testes manuais.",
            "Não alterar código da aplicação.",
            "Documentar falhas no README.md.",
        ],
    )
