from agno.models.ollama import Ollama
from agno.team import Team

from app.agent_back import backend_agent
from app.agent_front import frontend_agent


model = Ollama(id="mistral:7b")
members = [backend_agent, frontend_agent]

def create_team(backend_agent, frontend_agent):
    tech_lead = Team(
        name="Tech Lead",
        role="Coordenador de equipe de desenvolvimento de software",
        model=model,
        tools=[backend_agent, frontend_agent],
        members=[backend_agent, frontend_agent],
        instructions=[
            "Você é o Tech Lead responsável por coordenar a equipe de desenvolvimento.",
            "Divida as tarefas entre os agentes backend e frontend conforme necessário.",
            "Garanta que ambos os agentes sigam as melhores práticas de desenvolvimento.",
            "Revise o progresso dos agentes e forneça feedback construtivo.",
            "Assegure que a comunicação entre os agentes seja clara e eficiente."
        ],
        markdown=True
    )
    return tech_lead

