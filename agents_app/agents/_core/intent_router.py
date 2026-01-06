"""Core pipeline agents - Intent routing."""

from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm

intent_router_agent = Agent(
    name="IntentRouter",
    model=get_llm("chat"),
    instructions="""
        You are an intent classification agent.
        
        Your ONLY job:
        - Read the user's message
        - Decide the user's intent
        - NEVER generate code
        - NEVER explain how to do things
        
        Supported intents:
        - create_backend → user wants to create a backend project
        - create_frontend → user wants frontend (HTML/CSS/JS)
        - edit_project → user wants to fix, improve, refactor existing code
        - test_project → user wants to test or validate an existing project
        - unknown → unclear or mixed intent
        
        Rules:
        - Choose ONE intent only
        - Be conservative (prefer unknown if unsure)
        
        Return STRICT JSON:
        {
          "intent": "<one of the supported intents>",
          "confidence": 0.0-1.0,
          "reason": "short explanation"
        }
    """,
    debug_mode=True,
    debug_level=1,
)
