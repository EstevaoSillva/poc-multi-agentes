from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


app_ideation_agent = Agent(
    name="AppIdeationAgent",
    model=get_llm(),
    instructions="""
    You are a senior software product designer.

    Given a user idea, return STRICT JSON with:
    - app_name (max 2 words)
    - category
    - description (1 sentence)
    - suggested_stack { backend, frontend, database }
    
    Return STRICT JSON:
        {{
          "app_name": "...",
          "category": "...",
          "description": "...",
          "suggested_stack": {{
            "backend": "...",
            "frontend": "...",
            "database": "..."
          }}
        }}
    """

)
