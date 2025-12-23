from agno.models.ollama import Ollama
from agno.team import Team
from app.agent_back import backend_agent
from app.agent_front import frontend_agent
from app.researcher import researcher_agent

model = Ollama(id="mistral:7b")

tech_lead = Team(
    name="Tech Lead",
    role="Coordenador de equipe de desenvolvimento de software",
    model=model,
    members=[backend_agent, frontend_agent, researcher_agent],
    instructions=[
        "Você é o Tech Lead responsável por coordenar a equipe de desenvolvimento.",
        "Você não escreve código diretamente, mas supervisiona o trabalho dos engenheiros frontend e backend.",
        "Dependendo de qual pergunta que o usuario fizer, você delegará a tarefa para o engenheiro apropriado ou para o pesquisador web.",
        "Se a pergunta estiver relacionada ao desenvolvimento frontend, delegue para o engenheiro frontend.",
        "Se a pergunta estiver relacionada ao desenvolvimento backend, delegue para o engenheiro backend.",
        "É necessário que todas as respostas sejam em português.",
    ],
    markdown=True
)
