import os

from agno.models.groq import Groq
from agno.team import Team
from dotenv import load_dotenv

load_dotenv()

model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_TEAM_KEY")
)


def create_team(structure_agent, backend_agent, frontend_agent, test_agent):
    tech_lead = Team(
        name="Tech Lead",
        role="Coordenador de equipe de desenvolvimento de software",
        model=model,
        tools=[
            structure_agent,
            backend_agent,
            frontend_agent,
            test_agent
        ],
        members=[
            structure_agent,
            backend_agent,
            frontend_agent,
            test_agent
        ],
        instructions=[
            """
            Você é o Tech Lead responsável por orquestrar o pipeline de desenvolvimento.
            
            Fluxo obrigatório:
            1. Solicite ao agente de estrutura que crie as pastas e o contract.json
            2. Verifique se o arquivo contract.json existe
            3. Solicite aos agentes de backend e frontend que gerem código seguindo o contrato
            4. Solicite ao agente de testes que revise e execute os testes
            5. Consolide o resultado final
            
            Regras obrigatórias:
            - Nunca pule etapas
            - Nunca gere código diretamente
            - Sempre falhe se o contract.json não existir
            - Nunca assuma caminhos
            - Use apenas informações presentes no contract.json
            """
        ],
        markdown=True
    )
    return tech_lead
