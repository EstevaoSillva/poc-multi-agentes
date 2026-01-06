from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm


def frontend_infra_agent(frontend_dir):
    """
    Agent that generates the frontend infrastructure scaffold.

    Output (STRICT JSON):
    { "files": [{"path":"index.html","content":"..."}, ...], "run_commands": ["npm install"] }

    Rules:
    - Paths must be relative to `frontend_dir`.
    - Do NOT implement business logic or API integration here; infra provides the base files only.
    - Ensure UTF-8 encoding and include a README with run instructions.
    """

    return Agent(
        name="Frontend Infra Agent",
        role="Infraestrutura do frontend",
        model=get_llm("code"),
        instructions="""
            Create a minimal frontend scaffold. Return STRICT JSON only.

            Required files: `index.html`, `styles.css`, `app.js` (or an Angular minimal package.json if Angular requested).
            Include `README.md` with run steps and a sample `package.json` when appropriate.

            Keep files minimal and do not implement business logic or API calls.
        """,
        debug_mode=True,
        debug_level=2,
    )
