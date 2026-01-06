from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


def frontend_test_agent(frontend_dir):
    """
    Agent that validates frontend behavior and produces a test checklist and automated checks where possible.

    Output (STRICT JSON):
    { "files": [{"path":"tests/frontend_checklist.md","content":"..."}], "manual_checks": [...], "automated_commands": [...] }

    Rules:
    - Do not change application code; only produce tests and a checklist.
    - Validate fetch() usage and basic UI load behavior.
    """

    return Agent(
        name="Frontend Test Agent",
        role="Testes e validação do frontend",
        model=get_llm("code"),
        instructions="""
            Validate the frontend UI and produce a minimal automated test checklist and manual test steps.

            Return STRICT JSON only with `files` for any test/check artifacts and `manual_checks` for human validation.
        """,
        debug_mode=True,
        debug_level=2,
    )
