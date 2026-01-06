from pathlib import Path
from agno.team import Team
from agents_app.llm.ollama_provider import get_llm
from agents_app.agents.developer.frontend.infra import frontend_infra_agent
from agents_app.agents.developer.frontend.development import frontend_dev_agent
from agents_app.agents.developer.frontend.test import frontend_test_agent


def build_frontend_team(frontend_dir: Path = None):
    """
    Builds the Frontend Team with specialized agents.
    
    Args:
        frontend_dir: Base directory for frontend agents. Defaults to session workspace path.
    
    Returns:
        Team: Configured frontend team with agents in execution order.
    """
    if frontend_dir is None:
        frontend_dir = Path("./frontend")
    
    return Team(
        name="Frontend Team",
        role="Equipe de Frontend",
        model=get_llm("code"),
        members=[
            frontend_infra_agent(frontend_dir),
            frontend_dev_agent(frontend_dir),
            frontend_test_agent(frontend_dir),
        ],
        instructions=[
            "Execute members in order: Infra → Dev → Test.",
            "Each member must return STRICT JSON with a `files` list describing created/modified files.",
            "Frontend must use relative URLs to consume backend APIs."
        ],
    )
