import os
from pathlib import Path

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.file import FileTools
from agno.tools.shell import ShellTools
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_ROOT = PROJECT_ROOT / "my_app"

BASE_ROOT.mkdir(parents=True, exist_ok=True)

structure_model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_STRUCTURE_KEY")
)

structure_agent = Agent(
    name="Project Structure Agent",
    model=structure_model,
    tools=[FileTools(base_dir=BASE_ROOT)],
    instructions=[
        f"""
        Você é o ÚNICO agente autorizado a criar diretórios.

        Crie exatamente esta estrutura:
        - backend/
        - frontend/
        - test/
        - contract.json (na raiz)

        Regras absolutas:
        - Nunca use caminhos absolutos
        - Nunca crie arquivos fora de {BASE_ROOT}
        - Nunca gere código de aplicação
        - Nunca crie subpastas extras
        - Se algo já existir, sobrescreva
        - Gere um contract.json válido em JSON
        """
    ],
    debug_mode=True
)
