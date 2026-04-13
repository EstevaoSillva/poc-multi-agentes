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
        - Decide one intent
        - Return strict JSON only

        Supported intents:
        - create_backend
        - create_frontend
        - edit_project
        - test_project
        - auto_fix_project
        - unknown

        Rules:
        - Choose ONE intent only
        - Be conservative (prefer unknown if unsure)
        - confidence is a float from 0.0 to 1.0

        Return STRICT JSON:
        {
          "intent": "<supported_intent>",
          "confidence": 0.0,
          "reason": "short explanation"
        }
    """,
    debug_mode=True,
    debug_level=1,
)
