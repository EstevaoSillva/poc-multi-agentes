from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


def frontend_dev_agent(frontend_dir):
    """
    Agent to implement frontend UI and wire it to backend endpoints.

    Output (STRICT JSON):
    { "files": [{"path":"relative/path","content":"..."}, ...], "manual_checks": [] }

    Rules:
    - Use the stack declared in project context (Angular preferred if specified), otherwise use plain HTML/CSS/JS.
    - If using Angular, provide minimal `package.json` and `src` files; if plain, implement `index.html` + `app.js`.
    - Ensure all fetch() calls use relative URLs and match backend endpoints.
    - Do not modify infra files created by infra agent.
    """

    return Agent(
        name="Frontend Dev Agent",
        role="Desenvolvimento da interface",
        model=get_llm("code"),
        instructions="""
            Implement the UI for a Task list with full CRUD. Return STRICT JSON only with created/modified files.

            Ensure fetch() calls match backend endpoints and use relative URLs. Provide brief manual test checklist in `manual_checks`.
        """,
        debug_mode=True,
        debug_level=2,
    )
