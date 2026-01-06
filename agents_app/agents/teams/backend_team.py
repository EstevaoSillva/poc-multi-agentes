from pathlib import Path
from agno.team import Team
from agents_app.llm.ollama_provider import get_llm
from agents_app.agents.developer.backend.infra import backend_infra_agent
from agents_app.agents.developer.backend.database import backend_db_agent
from agents_app.agents.developer.backend.development import backend_dev_agent
from agents_app.agents.developer.backend.test import backend_test_agent


def build_backend_team(backend_dir: Path = None):
    """
    Builds the Backend Team with specialized agents.
    
    Args:
        backend_dir: Base directory for backend agents. Defaults to session workspace path.
    
    Returns:
        Team: Configured backend team with agents in execution order.
    """
    if backend_dir is None:
        backend_dir = Path("./backend")
    
    return Team(
        name="Backend Team",
        role="Equipe de Backend",
        model=get_llm("code"),
        members=[
            backend_infra_agent(backend_dir),
            backend_db_agent(backend_dir),
            backend_dev_agent(backend_dir),
            backend_test_agent(backend_dir),
        ],
        instructions=[
            "Executar na ordem: Infra → Database → Dev → Test.",
            "Each member must return STRICT JSON with a `files` array describing created/modified files.",
            "Do not perform destructive ops without explicit approval."
        ],
    )
