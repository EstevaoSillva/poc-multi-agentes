"""Teams orchestration module - multi-agent teams for coordinated execution."""

from agents_app.agents.teams.backend_team import build_backend_team
from agents_app.agents.teams.frontend_team import build_frontend_team
from agents_app.agents.teams.product_team import build_product_team

__all__ = [
    "build_backend_team",
    "build_frontend_team",
    "build_product_team",
]
