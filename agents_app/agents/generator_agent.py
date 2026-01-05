from agno.agent import Agent

from agents_app.llm.ollama_provider import get_llm

generator_agent = Agent(
    name="CodeGenerator",
    model=get_llm(),
    instructions="""
        You are a PROJECT GENERATOR, not just a code writer.
    
        Rules:
        - Every referenced directory MUST be created.
        - Every referenced file MUST exist.
        - The project MUST be runnable with:
          uvicorn main:app
    
        Forbidden:
        - Referencing directories that are not created.
        - Assuming folders exist.
        - Generating partial projects.
    
        Before finishing:
        - Validate the full file tree logically.
        """,
    debug_mode=True,
    debug_level=2,
)