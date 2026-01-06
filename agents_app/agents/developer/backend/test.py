from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


def backend_test_agent(backend_dir):
    """
    Agent that writes automated tests for the backend.

    Output (STRICT JSON):
    {
      "files": [ {"path":"tests/test_api.py","content":"..."}, ... ],
      "commands": ["pytest -q"]
    }

    Rules:
    - Do not change production code logic, only add tests and test helpers.
    - Tests should be minimal but runnable (use TestClient for FastAPI or Django test client).
    """

    return Agent(
        name="Backend Test Agent",
        role="Testes do backend",
        model=get_llm("code"),
        instructions="""
            Create automated pytest tests that validate the CRUD endpoints for the implemented resource.

            Return STRICT JSON only with `files` containing test files and a `commands` array with how to run them.
        """,
        debug_mode=True,
        debug_level=2,
    )