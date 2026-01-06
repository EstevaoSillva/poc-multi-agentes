from pathlib import Path
from agents_app.agents import test_agent
from agents_app.utils import safe_json_parse


class TestService:
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def run(self) -> dict:
        snapshot = self._snapshot()

        output = test_agent.run(snapshot)
        raw = output.content if hasattr(output, "content") else str(output)
        return safe_json_parse(raw)

    def _snapshot(self) -> str:
        files = []
        for file in self.workspace.rglob("*"):
            if file.is_file() and file.stat().st_size < 30_000:
                files.append(
                    f"\n### {file.relative_to(self.workspace)}\n{file.read_text(encoding='utf-8')}"
                )
        return "\n".join(files)