import os

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from dotenv import load_dotenv

load_dotenv()

db_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

def backend_db_agent(backend_dir):
    return Agent(
        name="Backend Database Agent",
        role="Banco de dados e ORM",
        model=db_model,
        tools=[FileTools(base_dir=backend_dir)],
        instructions=[
            "Configurar SQLite com SQLAlchemy.",
            "Usar Path(__file__) para caminho do banco.",
            "Criar models e engine.",
            "NÃO criar endpoints.",
        ],
    )

