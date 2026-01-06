from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


def backend_db_agent(backend_dir):
        """
        Agent responsible for database configuration and minimal ORM setup.

        Output contract (STRICT JSON):
        {
            "files": [ {"path":"relative/path","content":"..."}, ... ],
            "migration_commands": ["python manage.py makemigrations", ...] (optional)
        }

        Rules:
        - Prefer configuration using environment variables (provide .env.example).
        - If project uses Django, configure `DATABASES` to use Postgres via env vars and add minimal app `core` with `models.py`.
        - If project uses FastAPI, provide SQLAlchemy engine and `models.py` using an URL from env.
        - Do NOT create production data. Do NOT run commands — only return files and suggested commands.
        """

        return Agent(
                name="Backend Database Agent",
                role="Banco de dados e ORM",
            model=get_llm("code"),
                instructions="""
                        Configure database integration for the backend. Return STRICT JSON only.

                        Provide minimal files required to connect to a Postgres database via environment variables
                        and a small example model. Include a `.env.example` and a short `README.md` snippet explaining how to set DB URL.

                        Output JSON format:
                        {
                            "files": [
                                {"path": "core/models.py", "content": "..."},
                                {"path": ".env.example", "content": "..."}
                            ],
                            "migration_commands": ["python manage.py makemigrations", "python manage.py migrate"]
                        }

                        Constraints: Keep code minimal, framework-aware (Django vs FastAPI). Do not touch infra files.
                """,
                debug_mode=True,
                debug_level=2,
        )