from agno.agent import Agent

from agents_app.llm.ollama_provider import get_llm

planner_agent = Agent(
    name="PlannerAgent",
    model=get_llm(),
    instructions="""
        You are a senior software architect.
        
        Given a project context, create an execution plan.
        
        Return STRICT JSON:
        {
          "project_type": "web_app",
          "structure": {
            "frontend": ["src", "public"],
            "backend": ["src", "tests"],
            "shared": ["docs"]
          },
          "next_steps": [
            "Initialize backend project",
            "Initialize frontend project"
          ]
        }
        """
)