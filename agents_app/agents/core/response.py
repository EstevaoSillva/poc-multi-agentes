"""Core pipeline agents - Generic response generation."""

from agno.agent import Agent

from agents_app.llm.ollama_provider import get_llm


response_agent = Agent(
    name="ResponseAgent",
    model=get_llm("chat"),
    instructions="""
        You are a technical assistant for software project conversations.

        Rules:
        - Be concise and practical
        - Do not generate unrelated code
        - Focus on directly answering the user's request
    """,
    debug_mode=True,
    debug_level=1,
)
