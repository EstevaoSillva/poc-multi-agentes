from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


router_agent = Agent(
    name="IntentRouter",
    model=get_llm("chat"),
    instructions="""
        You are an intent classifier.
        
        Classify the user's request into ONE of the following intents:
        
        - CREATE_BACKEND_PROJECT
        - EDIT_EXISTING_PROJECT
        - TEST_PROJECT
        - AUTO_FIX_PROJECT
        - CHAT_ONLY
        
        Rules:
        - Return ONLY the intent string
        - No explanations
        - No markdown
        - No JSON
    """,
    debug_mode=True,
    debug_level=2
)