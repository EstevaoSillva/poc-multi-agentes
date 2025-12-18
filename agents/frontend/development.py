import os

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from dotenv import load_dotenv

load_dotenv()

dev_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

def frontend_dev_agent(frontend_dir):
    return Agent(
        name="Frontend Dev Agent",
        role="Desenvolvimento da interface",
        model=dev_model,
        tools=[FileTools(base_dir=frontend_dir)],
        instructions=[
            "Implementar interface de lista de tarefas.",
            "Usar apenas HTML5, CSS3 e JavaScript puro.",
            "Consumir API REST em http://127.0.0.1:8000.",
            "Implementar CRUD completo.",
            "Não alterar estrutura criada pelo Infra Agent.",
            "Não criar novos arquivos sem necessidade.",
            "Não criar README.",
        ],
    )
