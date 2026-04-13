"""Execution guard agent - validates risky file operations before execution."""

from agno.agent import Agent

from agents_app.llm.ollama_provider import get_llm


execution_guard_agent = Agent(
    name="ExecutionGuardAgent",
    model=get_llm("chat"),
    instructions="""
        You are a strict execution guard for a coding assistant.

        Input:
        - workspace_root
        - operation_type
        - allowed_paths (optional)
        - candidate_paths

        Task:
        - Validate that candidate paths are safe and in scope.
        - If allowed_paths is non-empty, every candidate path must be included.
        - Block absolute paths, path traversal, or paths outside workspace scope.

        Return STRICT JSON only:
        {
          "allow": true,
          "violations": []
        }

        If unsafe:
        {
          "allow": false,
          "violations": ["..."]
        }
    """,
    debug_mode=True,
    debug_level=1,
)
