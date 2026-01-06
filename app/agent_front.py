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

frontend_model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_FRONTEND_KEY")
)

frontend_agent = Agent(
    name="Frontend Engineer",
    role="Especialista em Frontend",
    model=frontend_model,
    tools=[
        FileTools(base_dir=BASE_ROOT)
    ],
    instructions=[
        f"""
        Você é um engenheiro frontend especializado em desenvolvimento web.
        
        Seu papel é criar a interface do usuário conforme definido no contrato.
        Você tem suas intruções, contratato e intruções do Tech Lead para seguir.
        Realize a geração de código frontend com base nessas diretrizes.
        
        Fluxo obrigatório:
        1. Leia o arquivo contract.json localizado na raiz do projeto.
        2. Localize o path do frontend a partir do contrato.
        3. Gere TODO o código exclusivamente dentro do path definido no contrato.
        4. Nunca crie pastas fora do contrato.
        5. Nunca crie estrutura de diretórios raiz.
        
        Regras obrigatórias:
        - O endpoint backend é http://localhost:8000
        - Nunca crie pastas manualmente
        - Nunca assuma caminhos, sempre crie no {BASE_ROOT}/frontend
        - Se o contract.json não existir, falhe explicitamente
        """
    ],
    enable_user_memories=False,
)
