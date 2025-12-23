from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools
from dotenv import load_dotenv
load_dotenv()



frontend_model = Ollama(
    id="mistral:7b",
)

frontend_agent = Agent(
    name="Frontend Engineer",
    role="Especialista em Frontend",
    model=frontend_model,
    instructions=[
        "Você é um engenheiro frontend especializado em desenvolvimento web.",
        "Seu trabalho é criar interfaces de usuário atraentes e responsivas que consumam APIs RESTful na porta 8000.",
        "Siga as melhores práticas de desenvolvimento frontend.",
        "Escreva código limpo, eficiente e bem documentado.",
        "Inclua um README.md com instruções claras sobre como configurar e executar o frontend.",
    ],
    debug_mode=True,
    debug_level=2,
    tools=[FileTools()],
    enable_user_memories=False,
)