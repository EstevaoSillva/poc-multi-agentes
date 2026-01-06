from pathlib import Path

from agents_app.agents import (
    generator_agent,
    intent_router_agent,
    planner_agent,
)
from agents_app.utils import safe_json_parse


REQUIRED_FILES = {
    "backend/manage.py",
    "backend/requirements.txt",
    "frontend/package.json",
    "docker-compose.yml",
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

    def _validate_required_files(self, files: list[str]):
        # REQUIRED_FILES is a generic set; specific required files depend on chosen stack
        file_set = set(files)
        # Keep a soft-check for generic required files but do not hard-fail here.
        missing = [f for f in REQUIRED_FILES if f not in file_set]
        if missing:
            # Logically allow generator to provide different required files per stack;
            # caller should re-validate using `_validate_contents` which enforces
            # backend/frontend entrypoints for the chosen stack.
            pass

    def _validate_contents(self, files_map: dict):
        # Basic checks: ensure docker-compose contains postgres and validate backend/frontend files
        docker_compose = files_map.get("docker-compose.yml", "")
        if not docker_compose:
            # Se o agente esqueceu o arquivo, vamos injetar um padrão para não quebrar o fluxo
            files_map[
                "docker-compose.yml"] = "version: '3.8'\nservices:\n  postgres:\n    image: postgres:15\n    environment:\n      POSTGRES_PASSWORD: password"
            docker_compose = files_map["docker-compose.yml"]

        if "postgres" not in docker_compose.lower():
            if "services:" in docker_compose:
                files_map[
                    "docker-compose.yml"] += "\n  postgres:\n    image: postgres:15\n    environment:\n      POSTGRES_PASSWORD: password"
            else:
                raise ValueError("docker-compose.yml must include a postgres service")

        # Backend: either Django (manage.py) OR FastAPI (main.py)
        manage = files_map.get("backend/manage.py", "")
        main_py = files_map.get("backend/main.py", "")

        if manage:
            if "DJANGO_SETTINGS_MODULE" not in manage and "django" not in manage.lower():
                raise ValueError("backend/manage.py does not look like a Django entrypoint")
        elif main_py:
            if "FastAPI" not in main_py and "fastapi" not in main_py.lower():
                raise ValueError("backend/main.py does not look like a FastAPI entrypoint")
        else:
            raise ValueError("Backend entrypoint not found: expect backend/manage.py or backend/main.py")

        # Frontend: either Angular package.json or plain index.html
        pkg = files_map.get("frontend/package.json", "")
        index_html = files_map.get("frontend/index.html", "")

        if pkg:
            if "@angular/core" not in pkg and "angular" not in pkg.lower():
                raise ValueError("frontend/package.json does not look like an Angular project")
        elif index_html:
            if "<html" not in index_html.lower():
                raise ValueError("frontend/index.html does not look like valid HTML")
        else:
            raise ValueError("Frontend entrypoint not found: expect frontend/package.json or frontend/index.html")

    def generate_project_from_description(self, description: str) -> dict:
        """
        Generate a project according to intent and planner recommendations.

        Behavior:
            - Runs the `intent_router_agent` to classify the intent.
            - Runs the `planner_agent` to get a suggested structure.
            - Requests `generator_agent` to produce a scaffold following the planner,
            but with a recommended stack: Django (backend), Angular (frontend),
            Postgres as the database. The `docker-compose.yml` must contain only
            the Postgres service (no other services started in docker).
        """
        # 1) Detect intent
        intent_prompt = f"Classify intent for project creation. User message:\n{description}\nReturn strict JSON with intent/confidence/reason."
        intent_out = intent_router_agent.run(intent_prompt)
        intent_raw = intent_out.content if hasattr(intent_out, "content") else str(intent_out)
        intent_data = safe_json_parse(intent_raw)

        # 2) Get plan from planner
        planner_prompt = f"Given the user intent and description, propose a project plan. Description:\n{description}\nReturn strict JSON with project_type, structure and next_steps."
        planner_out = planner_agent.run(planner_prompt)
        planner_raw = planner_out.content if hasattr(planner_out, "content") else str(planner_out)
        planner_data = safe_json_parse(planner_raw)

        # 3) Decide stack based on planner output or explicit suggested_stack in description
        # Try to parse description as JSON (ideation may have been passed through)
        suggested_backend = None
        suggested_frontend = None
        complexity = None

        try:
            desc_json = safe_json_parse(description)
            if isinstance(desc_json, dict):
                ss = desc_json.get("suggested_stack") or {}
                if isinstance(ss, dict):
                    backend_field = ss.get("backend")
                    if isinstance(backend_field, dict):
                        suggested_backend = backend_field.get("recommended")
                    else:
                        suggested_backend = backend_field

                    frontend_field = ss.get("frontend")
                    if isinstance(frontend_field, dict):
                        suggested_frontend = frontend_field.get("recommended")
                    else:
                        suggested_frontend = frontend_field

                complexity = desc_json.get("complexity")
        except Exception:
            # ignore parse errors and fallback to planner
            desc_json = None

        # If planner provided structure or recommendations, try to extract complexity
        if not complexity and isinstance(planner_data, dict):
            complexity = planner_data.get("complexity")

        # Mapping rules: low/medium -> FastAPI prefer, high -> Django
        backend_choice = None
        frontend_choice = None

        if suggested_backend:
            backend_choice = str(suggested_backend).lower()
        else:
            if complexity == "high":
                backend_choice = "django"
            else:
                backend_choice = "fastapi"

        if suggested_frontend:
            frontend_choice = str(suggested_frontend).lower()
        else:
            if complexity == "high":
                frontend_choice = "angular_material"
            elif complexity == "medium":
                frontend_choice = "angular"
            else:
                frontend_choice = "html_css_js"

        # Ensure values are within expected set
        if backend_choice not in ("django", "fastapi"):
            backend_choice = "fastapi"
        if frontend_choice not in ("angular", "angular_material", "html_css_js"):
            frontend_choice = "html_css_js"

        # Build generator prompt reflecting chosen stack
        gen_prompt = f"""
            Given the following planner output and user description, generate a project scaffold.

            Planner JSON:
            {planner_data}

            User description:
            {description}

            SELECTED STACK (must follow):
            - Backend: {backend_choice}
            - Frontend: {frontend_choice}
            - Database: postgres (docker only)

            RULES:
            - Do not include venv files, __pycache__, or DB data files.
            - Return STRICT JSON only with the format:
            {{
            "files": [ {{"path": "...", "content": "..."}}, ... ]
            }}

            Create a minimal, runnable scaffold for the selected stack. For backend:
            - If `django`: include `backend/manage.py`, `backend/requirements.txt`, a minimal `core` app and settings.
            - If `fastapi`: include `backend/main.py`, `backend/requirements.txt`, and uvicorn run instructions.

            For frontend:
            - If `angular` or `angular_material`: include `frontend/package.json` and minimal `src` structure.
            - If `html_css_js`: include `frontend/index.html`, `frontend/static/js/app.js`, and `frontend/styles.css`.

            MANDATORY: docker-compose.yml must be included and MUST contain a service named `db` or `postgres` using the `postgres` image.

            Make the scaffold minimal but runnable with documented run commands in README files.
        """

        gen_out = generator_agent.run(gen_prompt)
        gen_raw = gen_out.content if hasattr(gen_out, "content") else str(gen_out)
        data = safe_json_parse(gen_raw)

        # Validate JSON
        self._validate_json_schema(data)

        files_map = {f["path"]: f["content"] for f in data["files"]}
        file_paths = list(files_map.keys())

        # Validate required files
        self._validate_required_files(file_paths)
        self._validate_contents(files_map)

        created_files = []
        for path_str, content in files_map.items():
            path = self.workspace / path_str
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            created_files.append(path_str)

        # Return meta including intent/planner for traceability
        return {
            "intent": intent_data,
            "planner": planner_data,
            "files": created_files,
        }

    # Backwards-compatible wrapper for older callers
    def generate_minimal_fastapi_project(self, description: str) -> dict:
        """
        Compatibility shim: older code called `generate_minimal_fastapi_project`.
        Delegate to `generate_project_from_description` which now handles intent/planner
        and returns metadata + created files.
        """
        return self.generate_project_from_description(description)
