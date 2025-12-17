from agno.team import Team
from agno.models.groq import Groq
from teams.backend_team import build_backend_team
from teams.frontend_team import build_frontend_team

model = Groq(id="openai/gpt-oss-120b")

backend_team = build_backend_team(model)
frontend_team = build_frontend_team(model)

product_team = Team(
    name="Product Team",
    role="Coordenação geral",
    model=model,
    members=[backend_team, frontend_team],
    instructions=[
        "Executar backend primeiro.",
        "Após backend pronto, executar frontend.",
        "Garantir integridade do projeto.",
    ],
)
