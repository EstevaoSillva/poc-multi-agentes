import os

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.file import FileTools
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_ROOT = PROJECT_ROOT / "my_app"

if not BASE_ROOT.exists():
    raise RuntimeError(f"Base directory {BASE_ROOT} does not exist")

backend_model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_BACKEND_KEY")
)

backend_agent = Agent(
    name="Backend Engineer",
    role="Especialista em FastAPI",
    model=backend_model,
    tools=[
        FileTools(base_dir=BASE_ROOT)
    ],
    instructions=[
        f"""
        Você é um engenheiro backend especializado em FastAPI.
        
        Fluxo obrigatório:
        1. Leia o arquivo contract.json localizado na raiz do projeto.
        2. Localize o path do backend a partir do contrato.
        3. Gere TODO o código exclusivamente dentro do path definido no contrato.
        4. Nunca crie pastas fora do contrato.
        5. Nunca crie estrutura de diretórios raiz.
        
        Requisitos técnicos:
        - Utilize FastAPI e as boas práticas do framework
        - Gere a aplicação na porta 8000
        - Permita que o frontend consuma uma API RESTful (Porta aberta para CORS)
        - Crie um arquivo requirements.txt
        - Crie um README.md com instruções claras
        
        Regras obrigatórias:
        - Nunca crie pastas manualmente
        - Nunca assuma caminhos sempre crie no {BASE_ROOT}/backend
        - Se o contract.json não existir, falhe explicitamente
        """
    ]
)
