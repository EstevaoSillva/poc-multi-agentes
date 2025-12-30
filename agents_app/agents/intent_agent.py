from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm

intent_agent = Agent(
    name="IntentAgent",
    model=get_llm(),
    instructions="""
        Classify user intent:
        - READ
        - GENERATE
        - REVIEW
        - MODIFY
        - DELETE
        Return ONLY the intent.
        """
)
