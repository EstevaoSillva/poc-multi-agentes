from pathlib import Path
from agents_app.agents import editor_agent
from agents_app.utils import safe_json_parse


class EditorService:
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def edit(self, instruction: str) -> dict:
        project_snapshot = self._snapshot()

        prompt = f"""
            Project files:
            {project_snapshot}
            
            Task:
            {instruction}
        """

        output = editor_agent.run(prompt)
        raw = output.content if hasattr(output, "content") else str(output)
        data = safe_json_parse(raw)

        applied = []

        for change in data.get("changes", []):
            path = self.workspace / change["path"]

            if not path.exists():
                raise FileNotFoundError(f"{path} does not exist")

            path.write_text(change["content"], encoding="utf-8")
            applied.append(change["path"])

        return {"updated_files": applied}

    def _snapshot(self) -> str:
        result = []
        for file in self.workspace.rglob("*"):
            if file.is_file() and file.stat().st_size < 30_000:
                result.append(f"\n### {file.relative_to(self.workspace)}\n")
                result.append(file.read_text(encoding="utf-8"))
        return "\n".join(result)