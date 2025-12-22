import os
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.file import FileTools
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


FRONTEND_ROOT = Path("my_app/frontend").resolve()
FRONTEND_ROOT.mkdir(parents=True, exist_ok=True)

frontend_model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_FRONTEND_KEY")
)

frontend_agent = Agent(
    name="Frontend Engineer",
    role="Especialista em Frontend",
    model=frontend_model,
    instructions=[
        "Você é um engenheiro frontend especializado em desenvolvimento web usando HTML, CSS e JavaScript.",
        "Seu trabalho é criar interfaces de usuário atraentes e responsivas que consumam APIs RESTful na porta 8000.",
        "Siga as melhores práticas de desenvolvimento frontend.",
        "Escreva código limpo, eficiente e bem documentado.",
        "Inclua um README.md com instruções claras sobre como configurar e executar o frontend.",
        f"E importante que voce salve a aplicacao dentro da pasta '{FRONTEND_ROOT}', e que utilize caminhos relativos para referenciar os arquivos."
    ],
    debug_mode=True,
    debug_level=2,
    tools=[FileTools(base_dir=FRONTEND_ROOT)],
    enable_user_memories=False,
)