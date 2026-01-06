"""Core pipeline agents - Response formatting."""

from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


response_agent = Agent(
    name="ResponseAgent",
    model=get_llm(),
    instructions="""
        Summarize actions clearly.
        Never hallucinate.
    """
)
