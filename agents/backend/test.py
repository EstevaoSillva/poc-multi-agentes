import os

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.nvidia import Nvidia
from dotenv import load_dotenv

load_dotenv()

test_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

def backend_test_agent(backend_dir):
    return Agent(
        name="Backend Test Agent",
        role="Testes do backend",
        model=test_model,
        tools=[FileTools(base_dir=backend_dir), DuckDuckGoTools()],
        instructions=[
            "Criar testes com pytest.",
            "Testar CRUD.",
            "NÃO criar código de produção.",
        ],
    )

