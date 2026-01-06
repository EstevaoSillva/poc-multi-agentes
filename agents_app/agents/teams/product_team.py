from pathlib import Path
from agno.team import Team
from agents_app.llm.ollama_provider import get_llm
from agents_app.agents.teams.backend_team import build_backend_team
from agents_app.agents.teams.frontend_team import build_frontend_team


def build_product_team(session_workspace: Path = None):
    """
    Builds the Product Team that orchestrates Backend and Frontend teams.
    
    Args:
        session_workspace: Base directory for session. Defaults to current dir.
    
    Returns:
        Team: Configured product team with backend and frontend teams.
    """
    if session_workspace is None:
        session_workspace = Path(".")
    
    backend_dir = session_workspace / "backend"
    frontend_dir = session_workspace / "frontend"
    
    backend_team = build_backend_team(backend_dir)
    frontend_team = build_frontend_team(frontend_dir)
    
    return Team(
        name="Product Team",
        role="Coordenação geral",
        model=get_llm("code"),
        members=[backend_team, frontend_team],
        instructions=[
            "Execute backend team first, then frontend team.",
            "Ensure each team returns STRICT JSON with `files` and `status` fields.",
            "If any member reports an error, stop and report the failure.",
        ],
    )
