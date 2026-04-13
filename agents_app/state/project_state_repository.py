import json
from pathlib import Path
from typing import Dict, List


class ProjectStateRepository:
    def __init__(self, state_file: Path):
        """
        state_file: path to project_state.json
        """
        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.state_file.exists():
            self._write(self._initial_state())

    # ------------------------
    # Core IO
    # ------------------------

    def _initial_state(self) -> Dict:
        return {
            "completed_steps": [],
            "failed_steps": [],
            "generated_files": [],
            "last_step": None,
            "history": []
        }

    def _read(self) -> Dict:
        return json.loads(self.state_file.read_text(encoding="utf-8"))

    def _write(self, data: Dict):
        self.state_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    # ------------------------
    # Public API
    # ------------------------

    def get_state(self) -> Dict:
        return self._read()

    def mark_step_completed(self, step_name: str, files: List[str]):
        state = self._read()

        if step_name not in state["completed_steps"]:
            state["completed_steps"].append(step_name)

        state["last_step"] = step_name
        state["generated_files"].extend(files)

        state["history"].append({
            "step": step_name,
            "status": "completed",
            "files": files
        })

        self._write(state)

    def mark_step_failed(self, step_name: str, reason: str):
        state = self._read()

        state["failed_steps"].append(step_name)
        state["last_step"] = step_name

        state["history"].append({
            "step": step_name,
            "status": "failed",
            "reason": reason
        })

        self._write(state)

    def is_step_completed(self, step_name: str) -> bool:
        state = self._read()
        return step_name in state["completed_steps"]

    def reset(self):
        self._write(self._initial_state())