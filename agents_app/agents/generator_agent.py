from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


generator_agent = Agent(
    name="CodeGenerator",
    model=get_llm(),
    instructions=
        """
            Generate clean, production-ready code.
            Follow language best practices.
        """
)