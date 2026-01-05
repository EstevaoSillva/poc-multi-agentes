from pathlib import Path

from agents_app.agents.generator_agent import generator_agent
from agents_app.utils import safe_json_parse


class ProjectGeneratorService:
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def generate_minimal_fastapi_project(self, description: str) -> dict:
        prompt = f"""
            Generate a MINIMAL runnable FastAPI project.
            
            Application description:
            {description}
            
            Architecture:
            - Backend: FastAPI
            - Frontend: HTML5 + CSS
            - Database: SQLite
            
            Rules:
            - No authentication
            - No migrations
            - Minimal but runnable
            - Return ONLY valid JSON
            
            Return STRICT JSON:
            {{
              "files": [
                {{
                  "path": "backend/main.py",
                  "content": "..."
                }},
                {{
                  "path": "backend/requirements.txt",
                  "content": "..."
                }},
                {{
                  "path": "backend/database.py",
                  "content": "..."
                }},
                {{
                  "path": "backend/models.py",
                  "content": "..."
                }},
                {{
                  "path": "backend/templates/index.html",
                  "content": "..."
                }}
              ]
            }}
        """

        output = generator_agent.run(prompt)
        raw = output.content if hasattr(output, "content") else str(output)

        data = safe_json_parse(raw)

        created_files = []

        for file in data["files"]:
            path = self.workspace / file["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(file["content"], encoding="utf-8")
            created_files.append(file["path"])

        return {
            "files": created_files
        }
