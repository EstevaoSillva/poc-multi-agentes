import os

from agno.models.groq import Groq
from agno.team import Team
from dotenv import load_dotenv

load_dotenv()

model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_FRONTEND_KEY")
)


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

