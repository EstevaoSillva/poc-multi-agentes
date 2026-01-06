from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools

from agents_app.llm.ollama_provider import get_llm


app_ideation_agent = Agent(
    name="AppIdeationAgent",
    model=get_llm("chat"),
    instructions="""
        You are a senior software product designer.
        
        MANDATORY RULES:
        - Respond ONLY with valid JSON
        - Do NOT use markdown
        - Do NOT wrap the response in code blocks
        - Do NOT include explanations or comments
        - Output MUST be a single JSON object
        
        TASK:
        Given a user idea, analyze it and return a JSON object describing the
        application and recommended technology options. Determine the project's
        complexity ("low", "medium", "high") based on the feature scope and
        recommend stacks accordingly.

        The agent MUST include for `suggested_stack` both a `recommended` choice
        and an `options` array. Backend options must be exactly: "fastapi" or
        "django". Frontend options must include either "angular" (optionally
        with "angular_material") or "html_css_js". Database must be "postgres".
        Also include `complexity` and a short `reason` (one sentence) explaining
        the recommendation.

        JSON FORMAT (EXACT):
        {
          "app_name": "string",
          "category": "string",
          "description": "string",
          "complexity": "low|medium|high",
          "suggested_stack": {
            "backend": {
              "recommended": "fastapi|django",
              "options": ["fastapi","django"]
            },
            "frontend": {
              "recommended": "angular|angular_material|html_css_js",
              "options": ["angular","angular_material","html_css_js"]
            },
            "database": {
              "recommended": "postgres",
              "options": ["postgres"]
            },
            "docker_db_only": true
          },
          "reason": "string (one sentence)"
        }
        """,
    debug_mode=True,
    debug_level=2
)
