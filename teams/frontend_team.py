from agno.team import Team
from pathlib import Path
from agents.frontend.infra import frontend_infra_agent
from agents.frontend.dev import frontend_dev_agent
from agents.frontend.test import frontend_test_agent

def build_frontend_team(model):
    frontend_dir = Path("./my_app/frontend")

    return Team(
        name="Frontend Team",
        role="Equipe de Frontend",
        model=model,
        members=[
            frontend_infra_agent(model, frontend_dir),
            frontend_dev_agent(model, frontend_dir),
            frontend_test_agent(model, frontend_dir),
        ],
        instructions=[
            "Frontend estático.",
            "Consumir API do backend.",
        ],
    )
