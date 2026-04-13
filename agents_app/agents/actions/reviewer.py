from agno.agent import Agent

from agents_app.llm.ollama_provider import get_llm


reviewer_agent = Agent(
    name="ReviewerAgent",
    model=get_llm("code"),
    instructions="""
        You are a code reviewer.
        Analyze the generated code and return a concise technical review.
        Focus on correctness, obvious bugs, and risky assumptions.
        """,
    debug_mode=True,
    debug_level=1,
)
