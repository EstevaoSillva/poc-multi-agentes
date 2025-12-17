from agno.team import Team
from pathlib import Path
from agents.backend.infra import backend_infra_agent
from agents.backend.database import backend_db_agent
from agents.backend.dev import backend_dev_agent
from agents.backend.test import backend_test_agent

def build_backend_team(model):
    backend_dir = Path("./my_app/backend")

    return Team(
        name="Backend Team",
        role="Equipe de Backend",
        model=model,
        members=[
            backend_infra_agent(model, backend_dir),
            backend_db_agent(model, backend_dir),
            backend_dev_agent(model, backend_dir),
            backend_test_agent(model, backend_dir),
        ],
        instructions=[
            "Executar na ordem: Infra → Database → Dev → Test.",
            "Cada agente respeita sua responsabilidade.",
        ],
    )
