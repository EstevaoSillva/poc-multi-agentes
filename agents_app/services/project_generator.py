from pathlib import Path

from click import prompt

from agents_app.agents.generator_agent import generator_agent
from agents_app.utils import safe_json_parse


REQUIRED_FILES = {
    "backend/main.py",
    "backend/requirements.txt",
}

REQUIRED_DIRS = {
    "backend/templates",
    "backend/static",
    "backend/static/js",
}



class ProjectGeneratorService:
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def _validate_json_schema(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError("Output is not a JSON object")

        if "files" not in data or not isinstance(data["files"], list):
            raise ValueError("JSON must contain a 'files' list")

        for file in data["files"]:
            if "path" not in file or "content" not in file:
                raise ValueError("Each file must contain 'path' and 'content'")

            if not isinstance(file["path"], str) or not file["path"]:
                raise ValueError("Invalid file path")

            if not isinstance(file["content"], str):
                raise ValueError(f"Invalid content for file {file['path']}")


    def _validate_structure(self, files: list[str]):
        file_set = set(files)

        for required_file in REQUIRED_FILES:
            if required_file not in file_set:
                raise ValueError(f"Missing required file: {required_file}")

        for required_dir in REQUIRED_DIRS:
            if not any(f.startswith(required_dir + "/") for f in file_set):
                raise ValueError(f"Missing required directory: {required_dir}")


    def _validate_main_py(self, files: dict):
        content = files.get("backend/main.py", "")

        essential_snippets = [
            "FastAPI(",
        ]

        for snippet in essential_snippets:
            if snippet not in content:
                raise ValueError(f"main.py missing required snippet: {snippet}")


    def generate_minimal_fastapi_project(self, description: str) -> dict:
        prompt = f"""
            Based on the following project context and plan, generate the initial structure:
        
            {description}
            
            - DO NOT create virtual environments (venv), caches (__pycache__), or database files (.db, .sqlite).
            - Focus ONLY on the source code files and directory structure.
            
            You MUST return ONLY a JSON object with the following structure:

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

        # JSON
        self._validate_json_schema(data)

        files_map = {f["path"]: f["content"] for f in data["files"]}
        file_paths = list(files_map.keys())

        # Estrutura
        self._validate_structure(file_paths)

        # Conteúdo
        self._validate_main_py(files_map)

        created_files = []

        for path_str, content in files_map.items():
            path = self.workspace / path_str
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            created_files.append(path_str)

        return {"files": created_files}
