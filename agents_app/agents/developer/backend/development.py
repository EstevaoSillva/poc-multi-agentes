from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


def backend_dev_agent(backend_dir):
    """
    Agent responsible for implementing API endpoints and business logic.

    Output contract (STRICT JSON):
    {
      "files": [{"path":"relative/path","content":"..."}, ...],
      "tests": [{"path":"tests/test_api.py","content":"..."}] (optional)
    }

    Rules:
    - Detect existing framework (Django / FastAPI) and implement endpoints accordingly.
    - If Django: create a minimal API using Django REST Framework or Django views with JSON responses.
    - If FastAPI: create `main.py` with routes and Pydantic schemas.
    - Integrate with the database configuration previously provided; do not modify infra files.
    - Include minimal unit tests where appropriate.
    """

    return Agent(
        name="Backend Dev Agent",
        role="Desenvolvimento da API",
        model=get_llm("code"),
        instructions="""
            Implement a minimal, working set of API endpoints (CRUD) for a single resource (e.g., Task).

            Return STRICT JSON only with `files` containing all created/modified files and optional `tests`.

            Important constraints:
            - Paths are relative to the provided backend base directory.
            - Do not change infrastructure or database configuration files.
            - Ensure code is runnable and includes clear `run` instructions in README.md.
        """,
        debug_mode=True,
        debug_level=2,
    )