PLANNER_PROMPT = """
    {context}
    
        Rules:
        - Decide only ONE next action
        - Prefer execution over explanation
        - If no files exist, start by creating project structure
        - Return STRICT JSON only
        
        Possible intents:
        - create_project_structure
        - generate_backend
        - generate_frontend
        - generate_shared_code
        - explain_next_steps
        
        Respond with:
        {
          "strategy": "...",
          "intent": "...",
          "confidence": 0.0,
          "reason": "...",
          "tools": []
        }
    """

class PlannerAgent:
    def __init__(self, llm):
        self.llm = llm

    def run(self, context_prompt: str) -> dict:
        response = self.llm.generate(
            PLANNER_PROMPT.format(context=context_prompt)
        )

        return response
