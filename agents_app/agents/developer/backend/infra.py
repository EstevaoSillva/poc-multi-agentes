from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


def backend_infra_agent(backend_dir):
        """
        Agent that prepares the backend infrastructure scaffold.

        Contract: MUST return STRICT JSON object only. JSON format:
        {
            "files": [ {"path": "relative/path/in/backend_dir", "content": "..."}, ... ],
            "run_commands": ["pip install -r requirements.txt", ...] (optional)
        }

        Rules:
        - Paths must be relative to the provided `backend_dir`.
        - Do NOT create production data, virtualenvs, or __pycache__ entries.
        - Do NOT implement business logic, models or API endpoints (those belong to Dev agent).
        - Create minimal files to allow a developer to run the project locally.
        """

        return Agent(
                name="Backend Infra Agent",
                role="Infraestrutura do backend",
                model=get_llm("code"),
                instructions="""
                        Prepare a minimal, runnable backend scaffold. Return STRICT JSON only.

                        Required output JSON:
                        {
                            "files": [
                                {"path": "manage.py", "content": "..."},
                                {"path": "project/settings.py", "content": "..."},
                                {"path": "requirements.txt", "content": "..."},
                                {"path": "README.md", "content": "..."}
                            ],
                            "run_commands": ["python manage.py runserver"]
                        }

                        Additional constraints:
                        - Use environment variables for DB connection strings (provide .env.example).
                        - If a specific framework is requested in context (Django or FastAPI), produce scaffold for that framework.
                        - Do NOT create database migrations with real data.
                        - Keep files minimal and well-formed (UTF-8).
                """,
                debug_mode=True,
                debug_level=2,
        )