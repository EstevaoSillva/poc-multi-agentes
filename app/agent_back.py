from pathlib import Path

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from dotenv import load_dotenv

load_dotenv()



backend_model = Ollama(
    id="mistral:7b",
)

backend_agent = Agent(
    name="Backend Engineer",
    role="Especialiste em FastAPI",
    model=backend_model,
    tools=[FileTools()],
    instructions=[
        "Você é um engenheiro backend que tem grande gama em conhecimento de logica de negocio.",
        "Seu trabalho é criar e ensinar sobre APIs RESTful robustas e escaláveis.",
        "Siga as melhores práticas de desenvolvimento backend.",
        "Escreva código limpo, eficiente e bem documentado.",
        "Crie um arquivo requirements.txt com todas as dependências do projeto.",
        "Inclua um README.md com instruções claras sobre como configurar e executar o backend."
        "Sempre gere o endpoint na porta 8000."
    ],
    debug_mode=True,
    debug_level=2

)