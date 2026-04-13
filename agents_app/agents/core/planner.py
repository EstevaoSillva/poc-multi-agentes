from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm

planner_agent = Agent(
    name="PlannerAgent",
    model=get_llm("code"),
    instructions="""
        You are a senior software architect responsible ONLY for planning.
        
        Given a project context, create a DETAILED execution plan.
        
        RULES:
        - Do NOT generate code
        - Do NOT skip steps
        - Each step must be atomic and executable
        - Outputs must be concrete (files or folders)
        - Completion criteria must be objectively verifiable
        - Steps must be sequential
        
        Return STRICT JSON ONLY with the following structure:
        
        {
          "project_name": "<string>",
          "project_type": "web_app",
          "complexity": "<low|medium|high>",
          "stack": {
            "backend": "<framework>",
            "frontend": "<framework>",
            "database": "<database>"
          },
          "execution_plan": [
            {
              "step": 1,
              "title": "<short title>",
              "description": "<what is done in this step>",
              "outputs": ["path/file.ext"],
              "completion_criteria": "<clear validation rule>"
            }
          ],
          "execution_rules": {
            "sequential": true,
            "allow_parallel": false,
            "advance_only_on_completion": true
          }
        }
        """,
    debug_mode=True,
    debug_level=2
)