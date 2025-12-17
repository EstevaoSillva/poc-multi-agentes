import os
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.file import FileTools
from pathlib import Path


FRONTEND_ROOT = Path("my_app/frontend").resolve()
FRONTEND_ROOT.mkdir(parents=True, exist_ok=True)

frontend_model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_FRONTEND_KEY")
)

frontend_agent = Agent(
    name="Frontend Engineer",
    role="Especialista em UI",
    model=frontend_model,
    tools=[FileTools(base_dir=FRONTEND_ROOT)],
    enable_user_memories=False,
)