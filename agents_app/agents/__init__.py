"""Agents module - All agents for the multi-agent orchestration system.

Internal Structure (underscore prefix = internal/private):
- core: Core pipeline agents (intent routing, planning, response)
- actions: Action agents (generation, editing, review, testing)
- developer: Public - Specialized agents for backend/frontend development
- teams: Public - Team orchestration (Backend Team, Frontend Team, Product Team)

Public API (backward compatible):
- All agents are exported at package level
- Teams are available via build_* functions
"""

# Core agents from core module (internal)
from agents_app.agents.core.intent_router import intent_router_agent
from agents_app.agents.core.planner import planner_agent
from agents_app.agents.core.response import response_agent

# Action agents from actions module (internal)
from agents_app.agents.actions.generator import generator_agent
from agents_app.agents.actions.editor_agent import editor_agent
from agents_app.agents.actions.reviewer import reviewer_agent
from agents_app.agents.actions.test import test_agent

# Special agents (kept at root for backward compatibility)
from agents_app.agents.router_agent import router_agent
from agents_app.agents.app_ideation_agent import app_ideation_agent

# Developer agents (specialized)
from agents_app.agents.developer import (
    backend_infra_agent,
    backend_db_agent,
    backend_dev_agent,
    backend_test_agent,
    frontend_infra_agent,
    frontend_dev_agent,
    frontend_test_agent,
)

# Teams (agent orchestration)
from agents_app.agents.teams import (
    build_backend_team,
    build_frontend_team,
    build_product_team,
)

__all__ = [
    # Core agents
    "router_agent",
    "intent_router_agent",
    "planner_agent",
    "response_agent",
    "generator_agent",
    "reviewer_agent",
    "editor_agent",
    "test_agent",
    "app_ideation_agent",
    # Developer agents - backend
    "backend_infra_agent",
    "backend_db_agent",
    "backend_dev_agent",
    "backend_test_agent",
    # Developer agents - frontend
    "frontend_infra_agent",
    "frontend_dev_agent",
    "frontend_test_agent",
    # Teams
    "build_backend_team",
    "build_frontend_team",
    "build_product_team",
]
