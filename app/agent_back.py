import os
from agno.models.groq import Groq
from agno.agent import Agent
from agno.tools.file import FileTools # Ferramenta essencial para escrever código
from pathlib import Path


BACKEND_ROOT = Path("my_app/backend").resolve()
BACKEND_ROOT.mkdir(parents=True, exist_ok=True)

backend_model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_BACKEND_KEY")
)

backend_agent = Agent(
    name="Backend Engineer",
    role="Especialiste em FastAPI",
    model=backend_model,
    tools=[FileTools(base_dir=BACKEND_ROOT)],
    debug_mode=True,
    debug_level=2,
)