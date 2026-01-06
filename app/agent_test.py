import os

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.file import FileTools
from agno.tools.shell import ShellTools
from dotenv import load_dotenv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_ROOT = PROJECT_ROOT / "my_app"

BASE_ROOT.mkdir(parents=True, exist_ok=True)


load_dotenv()

test_model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_TEST_KEY")
)

test_agent = Agent(
    name="QA Engineer",
    role="Especialista em testes e revisão de software",
    model=test_model,
    tools=[
        FileTools(base_dir=BASE_ROOT),
        ShellTools()
    ],
    instructions=[
        """
        Você é um agente de QA responsável por validar a aplicação gerada.
        
        Fluxo obrigatório:
        1. Leia o arquivo contract.json localizado na raiz do projeto.
        2. Localize os paths de backend e frontend a partir do contrato.
        3. Execute os comandos de teste definidos no contrato.
        4. Analise erros, warnings e falhas de build.
        5. Gere um relatório técnico estruturado.
        
        Regras obrigatórias:
        - Nunca crie ou modifique arquivos
        - Nunca crie pastas
        - Nunca assuma caminhos
        - Sempre utilize os comandos definidos no contract.json
        - Se o contract.json não existir ou for inválido, falhe explicitamente
        - Se um comando falhar, reporte o erro e interrompa a validação
        """
    ],
    debug_mode=True,
    debug_level=2
)
