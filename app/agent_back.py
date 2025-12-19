from pathlib import Path

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools  # Ferramenta essencial para escrever código

BACKEND_ROOT = Path("my_app/backend").resolve()
BACKEND_ROOT.mkdir(parents=True, exist_ok=True)

backend_model = Ollama(
    id="mistral:7b",
)

backend_agent = Agent(
    name="Backend Engineer",
    role="Especialiste em FastAPI",
    model=backend_model,
    tools=[FileTools(base_dir=BACKEND_ROOT)],
    instructions=[
        "Você é um engenheiro backend especializado em FastAPI.",
        "Seu trabalho é criar APIs RESTful robustas e escaláveis.",
        "Siga as melhores práticas de desenvolvimento backend.",
        "Escreva código limpo, eficiente e bem documentado.",
        "Crie um arquivo requirements.txt com todas as dependências do projeto.",
        "Inclua um README.md com instruções claras sobre como configurar e executar o backend."
        f"E importante que voce salve a aplicacao dentro da pasta '{BACKEND_ROOT}', e que utilize caminhos relativos para referenciar os arquivos.",
        "Sempre gere o endpoint na porta 8000."

    ],
    debug_mode=True,
    debug_level=2

)