"""Action agents - Code review."""

from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


reviewer_agent = Agent(
    name="CodeReviewer",
    model=get_llm("chat"),
    instructions="""
        Review code for:
        - Bugs
        - Security
        - Performance
        - Style
        Return suggestions only.
    """
)
