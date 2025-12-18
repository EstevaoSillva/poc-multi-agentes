import os

from agno.models.ollama import Ollama
from agno.team import Team
from dotenv import load_dotenv

from teams.backend_team import build_backend_team
from teams.frontend_team import build_frontend_team

load_dotenv()

po_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

backend_team = build_backend_team()
frontend_team = build_frontend_team()

product_team = Team(
    name="Product Team",
    role="Coordenação geral",
    model=po_model,
    members=[backend_team, frontend_team],
    instructions=[
        "Executar backend primeiro.",
        "Após backend pronto, executar frontend.",
        "Garantir integridade do projeto.",
    ],
)
